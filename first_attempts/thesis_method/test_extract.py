def load_sentences(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

old_sentences = load_sentences("extractedSentences/chemicalsAquatic_thesis2010.txt")
new_sentences = load_sentences("extractedSentences/new_chemicalsAquatic_thesis2010.txt")

added = new_sentences - old_sentences
removed = old_sentences - new_sentences

print(f"Total in OLD: {len(old_sentences)}")
print(f"Total in NEW: {len(new_sentences)}")


for s in list(added)[:10]:
    print("-", s)