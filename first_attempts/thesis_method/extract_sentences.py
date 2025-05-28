import os
import spacy
from bs4 import BeautifulSoup
from chemicalTagging import (
    transformation_keywords, result_keywords, agent_keywords,
    condition_keywords, methodology_keywords
)

# Load SpaCy model with chemical NER
nlp = spacy.load("en_ner_bc5cdr_md")

# Setup
KEYWORDS = set(
    kw.lower() for group in (
        transformation_keywords, result_keywords, agent_keywords,
        condition_keywords, methodology_keywords
    ) for kw in group
)

def extract_sentences(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")

    extracted_sentences = []
    for p in soup.find_all("p"):
        text = p.get_text()
        doc = nlp(text)

        for sent in doc.sents:
            sent_text = sent.text.strip()
            sent_lower = sent_text.lower()

            has_chemical = any(ent.label_ == "CHEMICAL" for ent in doc.ents if ent.start >= sent.start and ent.end <= sent.end)
            has_keyword = any(kw in sent_lower for kw in KEYWORDS)

            if has_chemical and has_keyword:
                extracted_sentences.append(sent_text)

    return extracted_sentences

def process_all_tei(tei_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(tei_folder):
        if not file.endswith(".xml"):
            continue

        file_path = os.path.join(tei_folder, file)
        sentences = extract_sentences(file_path)

        out_path = os.path.join(output_folder, file.replace(".xml", ".txt"))
        #If the sentences list is empty, skip writing to the file
        if sentences == []:
            print(f"{file} → No sentences found, skipping file.")
            continue
        with open(out_path, "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(sentences))

        print(f"{file} → {len(sentences)} sentences saved to {out_path}")

if __name__ == "__main__":
    process_all_tei("teiFiles", "textFiles")
