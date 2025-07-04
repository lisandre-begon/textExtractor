#NOT USED YET When the results will be 

import json
from difflib import SequenceMatcher
from collections import Counter, defaultdict

PREDICTIONS_PATH = "./results/run_20250625_113821.json" 
THRESHOLD_PARTIAL = 0.6  # Similarity threshold for partial match classification

def load_data(path):
    with open(path) as f:
        return json.load(f)

def classify(pred, label):
    pred, label = pred.strip(), label.strip()
    if not pred:
        return "absent"
    elif pred == label:
        return "exact"
    else:
        ratio = SequenceMatcher(None, pred, label).ratio()
        if ratio >= THRESHOLD_PARTIAL:
            return "partial"
        else:
            return "wrong"

def analyse(preds):
    results = {
        "exact": 0,
        "partial": 0,
        "wrong": 0,
        "absent": 0,
        "total": 0
    }

    per_tag = defaultdict(Counter)

    for ex in preds:
        pred = ex["prediction"]
        label = ex["label"]
        classification = classify(pred, label)

        results[classification] += 1
        results["total"] += 1

        # analyse par tag si présent
        for tag, val in ex.get("tags", {}).items():
            per_tag[tag][classification] += 1
            per_tag[tag]["total"] += 1

    return results, per_tag

def print_results(results, per_tag):
    print("\nOverall Results:")
    for k in ["exact", "partial", "wrong", "absent", "total"]:
        print(f"{k:>8}: {results[k]}")

    print("\nPer Tag Results:")
    for tag, stats in per_tag.items():
        print(f"\nTag: {tag}")
        for k in ["exact", "partial", "wrong", "absent", "total"]:
            print(f"  {k:>7}: {stats[k]}")

def main():
    data = load_data(PREDICTIONS_PATH)
    results, per_tag = analyse(data)
    print_results(results, per_tag)

if __name__ == "__main__":
    main()
