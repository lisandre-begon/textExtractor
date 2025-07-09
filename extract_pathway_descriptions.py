import json

def extract_descriptions(json_file="envipathData/bbd.json", output_file="pathways_raw.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = []
    for p in data.get("pathways", []):
        name = p.get("name", "")
        desc = p.get("description", "")
        entries.append({
            "name": name,
            "description": desc
        })

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(entries, out, indent=2, ensure_ascii=False)

    print(f"✅ Exported {len(entries)} pathway descriptions to {output_file}")

if __name__ == "__main__":
    extract_descriptions()
