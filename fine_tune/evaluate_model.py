# fine_tune/evaluate_model.py

import json
from pathlib import Path
from datasets import load_dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Paths
MODEL_DIR = "./models/t5_finetuned"
TEST_PATH = "./data/test_data.json"
OUTPUT_PATH = "./results/predictions.json"

# Load model and tokenizer
model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)

# Load test data
dataset = load_dataset("json", data_files=TEST_PATH, split="train")

# Format and tokenize inputs
def preprocess(example):
    input_text = f"extract pathway json: {example['input']}"
    return tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

# Evaluate and generate predictions
results = []
for ex in dataset:
    encoded = preprocess(ex)
    output_ids = model.generate(**encoded, max_length=512)
    predicted = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    results.append({
        "input": ex["input"],
        "expected": ex["output"],
        "predicted": predicted
    })

# Save results
Path("./results").mkdir(exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f" Predictions saved to: {OUTPUT_PATH}")
