import os
import json
import re
import csv
import time
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF → text extraction
import spacy

# ✅ OUTPUT FOLDERS
INPUT_FILE = "pubmed_articles.csv"
PDF_DIR = "pdfs"
FILTERED_DIR = "filtered_sentences"
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(FILTERED_DIR, exist_ok=True)

# ✅ Sci-Hub Mirrors
SCI_HUB_MIRRORS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.hkvisa.net",
]

# ✅ Load SciSpaCy (chemical/biomedical model)
try:
    nlp_chem = spacy.load("en_ner_bc5cdr_md")
except Exception:
    nlp_chem = None

# ✅ Filtering Keywords & Patterns
CONDITION_KEYWORDS = [
    "soil", "sediment", "aqueous", "culture", "medium", "incubated", "temperature",
    "ph", "moisture", "light", "dark", "aerobic", "anaerobic", "half-life"
]
BIOLOGICAL_KEYWORDS = [
    "strain", "bacteria", "fungus", "yeast", "pseudomonas", "bacillus", "enzyme", "dehydrogenase", "oxidase"
]
NUMERIC_PATTERN = re.compile(r"\b(\d+\.?\d*\s*(%|days?|hours?|weeks?|°C|K|g/L|mg/L|µM|mM|ppm|ppb))\b", re.IGNORECASE)

# ✅ PDF Download Helper
def try_scihub_url(scihub_url):
    print(f"  └─ Access attempt : {scihub_url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(scihub_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f" X Loading fail (status {response.status_code})")
            return False, None

        soup = BeautifulSoup(response.content, "html.parser")
        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            print(f" X No PDF found in iframe")
            return False, None

        pdf_url = iframe["src"]
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif pdf_url.startswith("/"):
            parts = scihub_url.split("/")
            pdf_url = parts[0] + "//" + parts[2] + pdf_url

        return True, pdf_url
    except Exception as e:
        print(f"X Error trying to access {scihub_url} → {e}")
        return False, None

def try_all_scihub_mirrors(doi):
    for mirror in SCI_HUB_MIRRORS:
        scihub_url = f"{mirror}/{doi}"
        success, pdf_url = try_scihub_url(scihub_url)
        if success:
            return pdf_url
    return None

# ✅ PDF Text Extraction & Cleaning
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f" X Could not extract text from {pdf_path}: {e}")
        return ""

    # Basic cleaning: remove hyphenation, fix spacing
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"(\w)- (\w)", r"\1\2", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return text.strip()

# ✅ Sentence Filtering Functions
def split_text_into_sentences(text: str):
    return re.split(r'(?<=[.!?])\s+', text.strip())

def detect_chemicals(sentence: str) -> bool:
    if not nlp_chem:
        return False
    doc = nlp_chem(sentence)
    for ent in doc.ents:
        if ent.label_.lower() in ["chemical", "chemicalsubstance", "drug"]:
            return True
    return False

def detect_numeric(sentence: str) -> bool:
    return bool(NUMERIC_PATTERN.search(sentence))

def detect_conditions(sentence: str) -> bool:
    s_lower = sentence.lower()
    return any(word in s_lower for word in CONDITION_KEYWORDS)

def detect_biological_agents(sentence: str) -> bool:
    s_lower = sentence.lower()
    return any(word in s_lower for word in BIOLOGICAL_KEYWORDS)

def is_relevant_sentence(sentence: str) -> bool:
    return (
        detect_chemicals(sentence)
        or detect_numeric(sentence)
        or detect_conditions(sentence)
        or detect_biological_agents(sentence)
    )

def process_text_group_sentences(text):
    sentences = split_text_into_sentences(text)
    relevant_sentences = [s.strip() for s in sentences if s.strip() and is_relevant_sentence(s)]
    return relevant_sentences

# ✅ Main PDF Download & Immediate Processing
def main():
    print(" Downloading PubMed PDFs + Direct Filtering")
    logs = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = 0
        for row in reader:
            total += 1
            pmid = row.get("PMID")
            doi = row.get("DOI")
            title = row.get("Title", "").strip()[:100]
            pathway = row.get("PathwayName", "").strip()

            if not doi:
                print(f"[{pmid}] X No DOI found, skipping...")
                continue

            safe_pathway = re.sub(r"[^\w\-_\. ]", "_", pathway) or f"article_{pmid}"
            pdf_filename = f"{safe_pathway}__{pmid}.pdf"
            pdf_path = os.path.join(PDF_DIR, pdf_filename)

            filtered_filename = f"filtered_{safe_pathway}__{pmid}.txt"
            filtered_path = os.path.join(FILTERED_DIR, filtered_filename)

            # Skip if already processed
            if os.path.exists(filtered_path):
                print(f"Already processed: {filtered_filename}")
                continue

            print(f"\n[{pmid}] {title}")
            print(f"    DOI: {doi}")

            # Download PDF if not present
            if not os.path.exists(pdf_path):
                pdf_url = try_all_scihub_mirrors(doi)
                if pdf_url:
                    print(f"Downloading PDF from {pdf_url}")
                    try:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        pdf_response = requests.get(pdf_url, headers=headers, stream=True, timeout=20)
                        if pdf_response.status_code == 200:
                            with open(pdf_path, "wb") as f_out:
                                for chunk in pdf_response.iter_content(1024):
                                    f_out.write(chunk)
                            print(f"PDF downloaded: {pdf_path}")
                        else:
                            print(f" X Unable to download PDF (status {pdf_response.status_code})")
                            continue
                    except Exception as e:
                        print(f" X Error downloading PDF: {e}")
                        continue
                else:
                    print(f" X PDF not found on any Sci-Hub mirror")
                    continue

            # ✅ Extract text & filter immediately
            raw_text = extract_text_from_pdf(pdf_path)
            if not raw_text:
                print(f" X No text extracted from {pdf_filename}")
                continue

            filtered_sentences = process_text_group_sentences(raw_text)
            with open(filtered_path, "w", encoding="utf-8") as out:
                out.write("\n".join(filtered_sentences))

            print(f"✅ Filtered {len(filtered_sentences)} relevant sentences → {filtered_filename}")
            time.sleep(1.5)

    print("\n✅ All done! PDFs downloaded & filtered.")

if __name__ == "__main__":
    main()
