import pprint
import torch
from datasets import load_dataset
import pandas as pd

class HallucinationCalibrationLibrary:
    def __init__(self, dataset_name="pminervini/HaluEval", subset="general"):
        """
        Initializes the library using HaluEval.
        Subsets: 'general', 'summarization', 'qa', 'dialogue'
        """
        print(f"Loading {dataset_name} ({subset})...")
        self.subset = subset
        self.dataset = load_dataset(dataset_name, subset, split='data')
        self.library = []

    def build_calibration_set(self, num_samples=100):
        """
        Creates a list of dicts containing the 'Full' prompt and the 'Prior' prompt.
        Handles schema disparities between general and task-specific subsets dynamically.
        """
        for i in range(min(num_samples, len(self.dataset))):
            item = self.dataset[i]

            
            # 1. Dynamic Key Extraction based on HaluEval Subset Schema
            if "knowledge" in item and "question" in item:
                # Used in 'qa' and 'summarization' tasks
                context = item["knowledge"]
                query = item["question"]
            else:
                # Fallback for 'general' and 'dialogue' tasks
                context = item.get("knowledge", "No reference context provided.")
                query = item.get("user_query", item.get("question", ""))

            # 2. String Compilation
            full_prompt = f"Context: {context}\nQuestion: {query}\nAnswer:"

            # 3. The 'Prior' prompt is essentially just the question or empty context
            # to see what the model would say purely auto-regressively.
            prior_prompt = f"Answer the following: {query}\nAnswer:"


            
            # Dynamic Key Extraction for Ground Truth text
            if "right_answer" in item:
                # Standard for 'qa' subset
                right_text = item["right_answer"]
                hallucination_text = item["hallucination_answer"]
            elif "right_summary" in item:
                # Standard for 'summarization' subset
                right_text = item["right_summary"]
                hallucination_text = item["hallucination_summary"]
            else:
                # Standard for 'general' and 'dialogue' subsets
                # These subsets provide a single 'chatgpt_response' or 'model_response' 
                # and flag it with a 'hallucination' status ("yes" or "no").
                response_text = item.get("chatgpt_response", item.get("model_response", ""))
                is_hallucinated = item.get("hallucination", "").lower() == "yes"
                
                if is_hallucinated:
                    right_text = ""  # The dataset does not provide a corrected alternative
                    hallucination_text = response_text
                else:
                    right_text = response_text
                    hallucination_text = ""

            hallu = item.get("hallucination", "unknown")
            self.library.append({
                "id": i,
                "full_prompt": full_prompt,
                # "prior_prompt" : 
                "ground_truth_right": right_text,
                "ground_truth_hallucination": hallucination_text,
                "hallucinated": hallu,
            })
            
        print(f"Library built with {len(self.library)} samples.")
        return self.library


# =================================
# Test harness
# =================================
if __name__ == "__main__":
    # Test with general subset
    calib_lib = HallucinationCalibrationLibrary(subset="general")
    data = calib_lib.build_calibration_set(num_samples=200)

    prompts = []
    for item in data:
        prompt_dict = {}
        prompt_dict['prompt']       = f'"{item['full_prompt']}"'
        prompt_dict["hallucinated"] = item['hallucinated'].lower()
        prompts.append(prompt_dict)

    prompt_df = pd.DataFrame.from_records(prompts)        
       
    prompt_df.to_csv("prompt_library_pminervini_HaluEval.csv")

    print(prompt_df)

