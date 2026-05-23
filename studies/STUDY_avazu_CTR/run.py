#!/usr/bin/env python3

import git
import copy
import os , sys
from pathlib import Path
repo = git.Repo('.', search_parent_directories=True)
repo_root = repo.working_tree_dir
sys.path.insert(0, os.path.join(repo_root, "framework") )
sys.path.insert(0, os.path.join(repo_root, "studies/STUDY_avazu_CTR") )
from datetime import datetime
import utils

import numpy as np
import pandas as pd
import datagen
import networks
import trainer 
import hyper_parameters as hp 
import read_data as data_reader

# ===============================================================
# Create a standalone container for the experiment. 
# This container owns the entire experiemnt.
#   - Create dataset
#   - Creates models
#   - Trains models
#   - Evaluates models
# ===============================================================
class Golden:
    def __init__(self, args):
        self.args = args
        self.seed = 0xdeadbeef


        # Initialize model parameters
        self.model_type          = "lightgbm"
        self.model_cfg           = "lgbm_large"

        # Create output directory
        os.makedirs(self.args.outdir, exist_ok=True)


    # ============================================
    # Evaluate a single data slice
    # ============================================
    def evaluateSingleSlice(self, data, model_type, model_cfg ):
        split = hp.DEFAULT_DATA_SPLIT

        model = networks.build_model(model_type, model_cfg)
        t     = trainer.Trainer(model).verbose(False)

        # Hash categorical fields
        X,y, features = utils.hash_avazu_frame(data)

        # Train 
        # The trainer splits it internally into training_slice and holdout_slice.
        # Returns the heldout slice for 1) calibration and 2) validation
        history, (X_heldout, y_heldout)   = t.fit(X, y, split)     

        # Calibrate temperature
        # 1) Split holdout into calibration and final test
        calib_ratio = split["calib"] / (split["calib"] + split["test"])
        X_cal, X_test, y_cal, y_test = trainer.train_test_split(X_heldout, y_heldout, test_ratio = calib_ratio)

        print(f"X_cal : {X_cal.shape}, X_test {X_test.shape} {type(X_test)} {type(X_cal)}")  

        # First use final test slice to calculate raw F1 score. 
        # Also use the final test slice to evaluate the uncalibrated nll
        f1                          = t.evaluate_f1(X_test, y_test)
        nll_raw, model_score_raw    = t.evaluate_nll(X_test, y_test, temperature = 1.0)
        model_score_raw             = max(0.0, model_score_raw.item())

        # Now calibrate the temperature
        T = t.fit_temperature(X_cal, y_cal)

        # t now has a learned temperature.
        # Evaluate metric on calibrated data
        nll, model_score            = t.evaluate_nll(X_test, y_test, temperature = T)
        model_score                 = max(0.0, model_score)

        # store results
        result = {
            **model_cfg, 
            "temperature"   : T,             
            "f1"            : f1.item(),
            
            # Calibrated performance
            "model_score"   : model_score,
            "nll"           : nll,

            # Uncalibrated performance
            "model_score_raw"   : model_score_raw,
            "nll_raw"         : nll_raw,
        }
        return model, model_cfg, data, result


    # ============================================
    # Evaluate
    # ============================================
    def evaluate(self, accept_rule = lambda x: True ):

        results = []
        for data, start, end in data_reader.read_window(args.datadir):

            model, model_cfg, _, result = self.evaluateSingleSlice(
                                                            data,
                                                            "catboost",
                                                            hp.CATBOOST_LADDER["cat_large"]
            )
            print(result)
            results.append(result)


    # ============================================
    # Create models
    # ============================================
    def createGbt(self):
        # GBT                             = hp.GBT_SMALL
        # base_cfg                        = GBT[self.model_type]
        # model_cfg                       = copy.deepcopy(base_cfg)
        # model                           = networks.build_model(self.model_type, model_cfg)

        MODEL                           = hp.LIGHTGBM_LADDER
        base_cfg                        = MODEL[self.model_cfg]
        model_cfg                       = copy.deepcopy(base_cfg)
        model                           = networks.build_model(self.model_type, model_cfg)

        return model, model_cfg 

TEST_SETUP = Golden

# =====================================
# Test harness
# =====================================
if __name__ == "__main__":
    import argparse
    def loadArgs():
        default_output = os.path.join( Path(__file__).resolve().parent, "logs", datetime.now().strftime("%Y.%m.%d_%H.%M.%S")  )
        default_input  = os.path.join( Path(__file__).resolve().parent, "winsize_5h_stride_2h"  )
        ap = argparse.ArgumentParser()
        ap.add_argument(
            "--cached", 
            type=int, 
            required=False, 
            default=1 ,
            help = "Do not look in cache. Not to be used for regular operation"
        )

        ap.add_argument(
            "--datadir", 
            type=str, 
            required=False, 
            default=default_input ,
            help = f"Input directory from which data is read Default = {default_input}"
        )

        ap.add_argument(
            "--outdir", 
            type=str, 
            required=False, 
            default=default_input ,
            help = f"Output directory where result is stored. Default = {default_output}"
        )
        return  ap.parse_args()

    args      = loadArgs()
    test      = TEST_SETUP(args)
    result_df = test.evaluate()












