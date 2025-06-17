import json
import random
from pathlib import Path

# Define paths
raw_path = Path("data/raw_data.json")
train_path = Path("data/train_data.json")
test_path = Path("data/test_data.json")

# Load raw data
with raw_path.open() as f:
    data = json.load(f)

input_list = data["input"]
output_list = data["output"]

# Pair inputs with outputs
pairs = [
    {"input": inp["paragraph"], "output": json.dumps(out, ensure_ascii=False)}
    for inp, out in zip(input_list, output_list)
]

# Shuffle and split 80/20
random.shuffle(pairs)
split_idx = int(0.8 * len(pairs))
train_data = pairs[:split_idx]
test_data = pairs[split_idx:]

# Ensure output directories exist
train_path.parent.mkdir(parents=True, exist_ok=True)
test_path.parent.mkdir(parents=True, exist_ok=True)

# Save to files
with train_path.open("w") as f:
    json.dump(train_data, f, indent=2)
    print(f"Train data saved to: {train_path}")

with test_path.open("w") as f:
    json.dump(test_data, f, indent=2)
    print(f"Test data saved to: {test_path}")