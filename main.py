import os
import subprocess
from cleanTxt import process_text_file
from dotenv import load_dotenv
from extract_chemical_sentence import extract_chemical_sentence

# Load .env variables
load_dotenv()

PDF_FOLDER = os.getenv("PDF_FILES")
TEXT_FOLDER = os.getenv("TEXT_FILES")
CLEANED_FOLDER = os.getenv("TEXT_FILES_CLEANED")
EXTRACTED_FOLDER = os.getenv("EXTRACTED_SENTENCES")

# Check if any PDF files exist
if os.path.exists(PDF_FOLDER):
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if pdf_files:
        print(f"{len(pdf_files)} PDF file(s) found. Running extract_pdf.sh...")
        subprocess.run(["bash", "extract_pdf.sh"], check=True)
    else:
        print("No PDF files found. Skipping PDF extraction.")
else:
    print(f"PDF folder '{PDF_FOLDER}' not found.")


# Process each .txt file
for file in os.listdir(TEXT_FOLDER):
    if file.endswith(".txt"):
        file_path = os.path.join(TEXT_FOLDER, file)
        print(f"Cleaning: {file}")
        result = process_text_file(file_path, output_folder=CLEANED_FOLDER)
        cleaned_path = result["output_path"]
        print(f"Cleaned saved to: {cleaned_path} | Format: {result['mode']}")

        print("Extracting chemical sentences...")
        sentences = extract_chemical_sentence(cleaned_path)

        output_sent_path = os.path.join(EXTRACTED_FOLDER, file)
        with open(output_sent_path, "w", encoding="utf-8") as out:
            out.write("\n".join(sentences))

        print(f"Saved {len(sentences)} sentences to: {output_sent_path}")
