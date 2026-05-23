#!/usr/bin/env python3

import git
import copy
import os , sys
from pathlib import Path
repo = git.Repo('.', search_parent_directories=True)
repo_root = repo.working_tree_dir
sys.path.insert(0, os.path.join(repo_root, "framework") )
from datetime import datetime

import numpy as np
import pandas as pd
import datagen
import networks
import trainer 
import hyper_parameters as hp 

# ===============================================================
# Create a standalone container for the experiment. 
# This container owns the entire experiemnt.
#   - Create dataset
#   - Creates models
#   - Trains models
#   - Evaluates models
# ===============================================================
class MLP_FixedDepth:
    def __init__(self, args):
        self.args = args
        self.seed = 0xdeadbeef
        self.datafilename = "bernoulli_data.npz"

        # Feature distribution
        self.feature_distribution =[
                {"dims": 4, "dist": "gaussian", "scale": 1.5},   # strong signal region
                {"dims": 2, "dist": "gaussian", "scale": 1.0},   # strong signal region
                {"dims": 3, "dist": "gaussian", "scale": 0.25},  # weak signal region
                {"dims": 5, "dist": "uniform",  "scale": 1.0},   # nuisance / different geometry U(-1, 1)
                {"dims": 5, "dist": "uniform",  "scale": 5.0},   # nuisance / different geometry U(-5, 5)
                {"dims": 6, "dist": "laplace",  "scale": 1.0},   # nuisance / different geometry
            ]
        self.num_dim     = sum([item["dims"] for item in self.feature_distribution])
        self.num_examples= 5000        # Number of example data points for each dataset

        # Learnability control: Noise scale
        # self.beta        = list(np.logspace(-0.1, 1.0, 100)) 
        self.beta = list(np.logspace(-0.2, 1.0, 25))
        
        # Learnability control: Number of active dimensions to be kept. Rest are zeroed out to make feature set sparse
        self.active_perc = [10,  50,   100]

        # Initialize the generator
        self.ensemble = datagen.BernoulliLearnabilityEnsemble(
            d    = self.num_dim,
            N    = self.num_examples,
            beta = self.beta,
            active_dims    = [int(np.ceil(item * self.num_dim / 100)) for item in self.active_perc],
            feature_blocks = self.feature_distribution,
            seed           = self.seed,
        )

        # Initialize model parameters
        self.model_type          = "mlp"
        # self.HIDDEN_LAYER_WIDTHS =  list(np.arange(32, 512, 16))  
        self.HIDDEN_LAYER_WIDTHS = [32, 64, 96, 128, 160, 192, 256, 320, 384, 512, 640, 768, 896, 1024]
        self.DROPOUT             = 0.1

        # Create output directory
        os.makedirs(self.args.outdir, exist_ok=True)

    # ============================================
    # Evaluate
    # ============================================
    def evaluate(self, accept_rule = lambda x: True ):
        results = []
        for d in self.ensemble.generate():
            data                        = d.serialize()
            num_features                = data["d"]
            L_true                      = data["learnability_true"]

            if not accept_rule(L_true): continue

            for width in self.HIDDEN_LAYER_WIDTHS:
                model, model_cfg            = self.createMlp(num_features, width, self.DROPOUT)
                t                           = trainer.Trainer(model).verbose(False)
                
                # Train 
                # The trainer splits it internally into training_slice and holdout_slice.
                # Returns the heldout slice for 1) calibration and 2) validation
                history, (X_heldout, y_heldout)   = t.fit(data["X"], data["y"])

                # Calibrate temperature
                # 1) Split holdout into calibration and final test
                X_cal, X_test, y_cal, y_test = trainer.train_test_split(X_heldout, y_heldout, test_ratio=0.5)                

                # First use final test slice to calculate raw F1 score. 
                # Also use the final test slice to evaluate the uncalibrated nll
                f1                          = t.evaluate_f1(X_test, y_test)
                nll_raw, model_score_raw    = t.evaluate_nll(X_test, y_test, temperature = 1.0)
                model_score_raw             = max(0.0, model_score_raw.item())
                efficiency_raw              = model_score_raw / L_true

                # Now calibrate the temperature
                T = t.fit_temperature(X_cal, y_cal)

                # t now has a learned temperature.
                # Evaluate metric on calibrated data
                nll, model_score            = t.evaluate_nll(X_test, y_test, temperature = T)
                model_score                 = max(0.0, model_score)
                efficiency                  = model_score / L_true

                # store results
                result = {
                    **model_cfg, 
                    "dataset"       : data["name"],
                    "L_true"        : L_true,
                    "temperature"   : T,             
                    "f1"            : f1.item(),
                    
                    # Calibrated performance
                    "model_score"   : model_score,
                    "efficiency"    : efficiency.item(),
                    "nll"           : nll,

                    # Uncalibrated performance
                    "model_score_raw"   : model_score_raw,
                    "efficiency_raw"    : efficiency_raw,
                    "nll_raw"         : nll_raw,
                }
                print(result)
                results.append(result)

        # Create dataframe of results
        df = pd.DataFrame( results )

        # Save to excel
        outfile = os.path.join(self.args.outdir, "results.xlsx")
        with pd.ExcelWriter(outfile) as writer:
            df.to_excel(writer, sheet_name="summary")
        
        print(f"Written results in {outfile}")
        return df, outfile

    # ============================================
    # Create models
    # ============================================
    def createMlp(self, num_features, width, dropout):
        MLP                             = hp.MLP_SMALL
        base_cfg                        = MLP[self.model_type]
        model_cfg                       = copy.deepcopy(base_cfg)
        model_cfg["hidden_layer_width"] = width
        model_cfg["dropout"]            = dropout
        model_cfg["input_dim"]          = num_features
        model_cfg["out_classes"]        = 2
        model = networks.build_model(self.model_type, model_cfg)
        return model, model_cfg 

TEST_SETUP = MLP_FixedDepth

# =====================================
# Test harness
# =====================================
if __name__ == "__main__":
    import argparse
    def loadArgs():
        default_output = os.path.join( Path(__file__).resolve().parent, "logs", datetime.now().strftime("%Y.%m.%d_%H.%M.%S")  )
        ap = argparse.ArgumentParser()
        ap.add_argument(
            "--cached", 
            type=int, 
            required=False, 
            default=1 ,
            help = "Do not look in cache. Not to be used for regular operation"
        )  

        ap.add_argument(
            "--outdir", 
            type=str, 
            required=False, 
            default=default_output ,
            help = f"Output directory where result is stored. Default = {default_output}"
        )
        return  ap.parse_args()

    args      = loadArgs()
    test      = TEST_SETUP(args)
    result_df = test.evaluate()












