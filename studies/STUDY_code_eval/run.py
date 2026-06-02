
# Get root of the repo
import subprocess
import sys, os
import pandas as pd
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
import datetime
from pypdf import PdfWriter

def get_git_root():
    try:
        # Run the git command and capture the output
        output = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT)
        return output.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        # Not a git repository or git is not installed
        return None



###############################################################
# Load project
###############################################################
ROOT=get_git_root()
assert ROOT, "Invalid git repository"
PROJECT = os.path.join(ROOT, "resource_aware_inference")
sys.path.insert(0,  PROJECT)
print(f"Repository root at   {ROOT}")
print(f"Loading project from {PROJECT}")


###############################################################
# Experiment
###############################################################
# import mech_interp_base  as mint

import mech_interp_transformerlens  as mint
import utils

import argparse

def run(args):
    # model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    # model_name = "Qwen/Qwen2.5-7B-Instruct"

    model_name        = args.model
    DEVICE            = args.device
    MAX_OUTPUT_TOKENS = args.max_output_tokens
 
    # =====================================================
    # Output directory
    # =====================================================
    default_output = os.path.join( Path(__file__).resolve().parent, "logs", model_name,  datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")  )
    os.makedirs(default_output, exist_ok=True)
    print(f"Created output directory at {default_output}")

    # =====================================================
    # The prompts
    # =====================================================
    df = pd.read_csv(args.prompt_csv)


    # ===================================================================
    # The model
    # ===================================================================
    tracker = mint.InferenceHealthTracker(
        model_name            = model_name,
        device                = DEVICE,
        prior_window          = 64,
        enable_internal_probe = not args.disable_internal_probe,
    )

    # ===================================================================
    # Run prompts
    # ===================================================================
    results = []

    merger = PdfWriter()
    # for idx, prompt in enumerate(prompts):
    for row in df.itertuples():
        prompt = row.prompt
        idx    = row.task_id
        outdir = os.path.join(default_output, f"prompt_{idx}")
        os.makedirs(outdir , exist_ok=True)

        tracker.reset()

        # temporary handle
        temp_pdffile   = os.path.join(outdir,  f"inference_health_prompt.pdf")
        temp_pdfhandle = PdfPages(temp_pdffile)


        # Inferencing step
        print("="*60)
        print("Inferencing...")
        print("PROMPT:")
        print(prompt)
        result = tracker.generate(
            prompt=prompt,
            max_new_tokens = MAX_OUTPUT_TOKENS,
            temperature=0.0,
        )

        # Store model output
        print("MODEL OUTPUT:")
        model_out_text = result["text"]
        print(model_out_text)
        with open(os.path.join(outdir, "response.py"), "w") as f: f.write(model_out_text)


        # Grab data for each step.
        # For each step, grab the final logit stats, and
        # the stats for each hidden layer.
        DJS = []
        layer_entropy = []
        attention_spectral_records = []
        mlp_gating_records = []
        residual_update_records = []
        for step in result["trace"]:
            # Truncate text to 20 chars and align left
            text = step['token_text'][:20]
            
            # Handle the 'None' case for logp_prior to avoid float formatting errors
            log_posterior = step['logp_full']
            posterior     = np.exp(log_posterior)
            log_prior     = step['logp_prior']
            prior         = np.exp(log_prior) if log_prior is not None else None
            prior_string  = f"{prior:<30.6f}" if prior is not None else f"{'None':<30}"

            if step["layerstats"]:
                DJS.append ( [item.D_js for item in step["layerstats"]] )
                layer_entropy.append ( [item.layer_entropy for item in step["layerstats"]] )

            # InternalProber records are experiment-facing telemetry.  They are
            # intentionally flattened here rather than inside the model wrapper so
            # future experiments can choose their own aggregation / clustering.
            probe_record = step.get("internal_probe")
            if probe_record:
                flat_probe = tracker.internal_prober.flatten_probe_record(probe_record)
                for rec in flat_probe.get("attention_spectral_stats", []):
                    rec["step_idx"] = len(DJS) - 1
                    rec["token_text"] = step["token_text"]
                    attention_spectral_records.append(rec)
                for rec in flat_probe.get("mlp_gating_stats", []):
                    rec["step_idx"] = len(DJS) - 1
                    rec["token_text"] = step["token_text"]
                    mlp_gating_records.append(rec)
                for rec in flat_probe.get("residual_update_stats", []):
                    rec["step_idx"] = len(DJS) - 1
                    rec["token_text"] = step["token_text"]
                    residual_update_records.append(rec)

        # Jensen-Shannon divergence num_tokens x num_layers
        DJS_df           = pd.DataFrame.from_records(DJS)    
        layer_entropy_df = pd.DataFrame.from_records(layer_entropy)     

        result["DJS"]           = DJS_df
        result["layer_entropy"] = layer_entropy_df

        result["attention_spectral"] = pd.DataFrame.from_records(attention_spectral_records)
        result["mlp_gating"]         = pd.DataFrame.from_records(mlp_gating_records)
        result["residual_update"]    = pd.DataFrame.from_records(residual_update_records)

        # Persist experiment-facing telemetry for downstream clustering / trajectory
        # distance work without changing mech_interp_transformerlens.py.
        result["attention_spectral"].to_csv(os.path.join(outdir, f"attention_spectral.csv"), index=False)
        result["mlp_gating"].to_csv(os.path.join(outdir, f"mlp_gating.csv"), index=False)
        result["residual_update"].to_csv(os.path.join(outdir, f"residual_update.csv"), index=False)

        # Aggregate    
        results.append(result)

        # Save to PDF
        mint.plotPmi( [result], temp_pdfhandle)
        temp_pdfhandle.close()

        merger.append(temp_pdffile)
        print(f"Saved PDF file for prompt {idx} at {temp_pdffile}")


    # Final merged PDF file
    pdffile   = os.path.join(default_output,  "inference_health.pdf")
    with open(pdffile, "wb") as f:
        merger.write(f)
    print(f"Saved PDF report to: {pdffile}") 



###############################################################
# Entry
###############################################################
if __name__ == "__main__":
    def parseArgs():
        ap=argparse.ArgumentParser()
        ap.add_argument(
            "--model", 
            required=False, 
            default = "mistralai/Mistral-7B-Instruct-v0.1", 
            help    = "Open source LLM. Eg (mistralai/Mistral-7B-Instruct-v0.3)"
        )

        ap.add_argument(
            "--prompt_csv", 
            required=False, 
            default = os.path.join(PROJECT, "prompt_library_pminervini_HaluEval.csv"),
            help = "CSV file containing prompts. Schema: 'prompt': str, 'hallucinated':str (yes/no)  "
        )

        ap.add_argument(
            "--device", 
            required=False, 
            default = "mps",
            help = "Device to run on: mps or cpu"
        )

        ap.add_argument(
            "--max_output_tokens", 
            required=False, 
            default = 500,
            type = int,
            help = "Each prompt generates upto these many tokens"
        )

        ap.add_argument(
            "--disable_internal_probe",
            action="store_true",
            help="Disable InternalProber collection for faster legacy runs."
        )
        args=ap.parse_args()
        return args


    args = parseArgs()
    run(args)










    









