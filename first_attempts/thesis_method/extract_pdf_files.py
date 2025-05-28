# New method to extract text from PDF files using Grobid 
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PDF_FOLDER = Path(os.getenv("PDF_FILES"))
TEXT_FOLDER = Path(os.getenv("TEXT_FILES"))
TEXT_FOLDER.mkdir(parents=True, exist_ok=True)

for pdf_path in PDF_FOLDER.glob("*.pdf"):
    print(f"Processing: {pdf_path.name}")
    try:
        with open(pdf_path, 'rb') as f:
            response = requests.post(
                "http://localhost:8070/api/processFulltextDocument",
                files={'input': f}
            )

        if response.status_code == 200:
            output_path = TEXT_FOLDER / pdf_path.with_suffix(".tei.xml").name
            with open(output_path, "wb") as out_file:
                out_file.write(response.content)
            print(f" Saved: {output_path.name}")
            pdf_path.unlink()  # delete the original PDF
        else:
            print(f" Failed ({response.status_code}) on {pdf_path.name}")
    except Exception as e:
        print(f" Error on {pdf_path.name}: {e}")
