import json
#Script to organised my data into { {input, output}, ... }
with open("pathway_paragraph.json") as f:
    data = json.load(f)

input_list = data["input"]
output_list = data["output"]

pairs = []
for inp, out in zip(input_list, output_list):
    pairs.append({
        "input": inp["paragraph"],
        "output": json.dumps(out, ensure_ascii=False)
    })

with open("train_data.json", "w") as f:
    json.dump(pairs, f, indent=2)
