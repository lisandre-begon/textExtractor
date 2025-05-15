import os
import subprocess
from dotenv import load_dotenv
from extract_sentences import process_all_tei

# Load .env variables
load_dotenv()

PDF_FOLDER = os.getenv("PDF_FILES")
TEI_FOLDER = os.getenv("TEI_FILES")
TEXT_OUTPUT_FOLDER = os.getenv("TEXT_FILES")

# Step 1: Check for PDFs → Run Grobid if needed
if os.path.exists(PDF_FOLDER):
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if pdf_files:
        print(f"{len(pdf_files)} PDF file(s) found. Running Grobid PDF → TEI conversion...")
        subprocess.run(["python3", "extract_pdf_files.py"], check=True)
    else:
        print("No PDF files found. Skipping PDF extraction.")
else:
    print(f"PDF folder '{PDF_FOLDER}' not found.")

# Step 2: Extract chemical sentences from TEI XML files
if os.path.exists(TEI_FOLDER):
    print(f"Extracting sentences from TEI files in '{TEI_FOLDER}'...")
    process_all_tei(TEI_FOLDER, TEXT_OUTPUT_FOLDER)
else:
    print(f"TEI folder '{TEI_FOLDER}' not found.")
