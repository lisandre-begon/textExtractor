import os
import re
import fitz #Will still work, the ide does not recognize it

def clean_scihub_pdfs(pdfs_folder_path, clean_pdfs_folder_path):
    if not os.path.exists(clean_pdfs_folder_path):
        os.makedirs(clean_pdfs_folder_path)

    for filename in os.listdir(pdfs_folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdfs_folder_path, filename)
            clean_pdf_path = os.path.join(clean_pdfs_folder_path, filename.replace('.pdf', '.txt'))

            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()

            text = re.sub(r'\n+', ' ', text)               # merge multiple newlines into a single space
            text = re.sub(r'(\w)- (\w)', r'\1\2', text)    # fix hyphenation at line breaks
            text = re.sub(r'\s{2,}', ' ', text)            # collapse multiple spaces
            text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # add missing space between 2 words

            with open(clean_pdf_path, 'w', encoding='utf-8') as clean_pdf_file:
                clean_pdf_file.write(text)

            print(f" Cleaned {filename} → {clean_pdf_path}")

if __name__ == "__main__":
    clean_scihub_pdfs("pdfs", "clean_pdfs")