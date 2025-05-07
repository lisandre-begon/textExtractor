import spacy

# Load the spaCy model
nlp = spacy.load("en_ner_bc5cdr_md")

def extract_chemical_sentence(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc = nlp(text)
    sentences_with_chemicals = []
    
    for sent in doc.sents:
        # Check if the sentence contains any chemical entities
        if any(ent.label_ == "CHEMICAL" and ent.start >= sent.start and ent.end <= sent.end for ent in doc.ents):
            sentences_with_chemicals.append(sent.text.strip())
    return sentences_with_chemicals
