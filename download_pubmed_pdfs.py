import os
import json
import re
import csv
import time
import requests
from bs4 import BeautifulSoup
import webbrowser

INPUT_FILE = "pubmed_articles.csv"
OUTPUT_DIR = "pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#We test all the diffrent sci hub mirrors to be sure we can access the PDF
SCI_HUB_MIRRORS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.hkvisa.net",
]
#Fucntion where we try to access the PDF via the Sci-Hub urls
def try_scihub_url(scihub_url):
    print(f"  └─ Access attempt : {scihub_url}")
    try:
        #We mimic the browser user agent to avoid blocks frm the site
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
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

        print(f"PDF found : {pdf_url}")
        return True, pdf_url
    except Exception as e:
        print(f"X Error trying to access {scihub_url} → {e}")
        return False, None

def try_all_scihub_mirrors(doi):
    print(f"Search PDF by DOI : {doi}")
    for mirror in SCI_HUB_MIRRORS:
        scihub_url = f"{mirror}/{doi}"
        success, pdf_url = try_scihub_url(scihub_url)
        if success:
            print(f"PDF found by {mirror}")
            return pdf_url
    print(f"X None of the Sci-Hub mirrors could access the PDF for DOI {doi}")
    return None

def main():
    print(" Downloading PubMed PDFs from Sci-Hub")
    logs = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = 0
        downloaded = 0
        for row in reader:
            total += 1
            pmid = row.get("PMID")
            doi = row.get("DOI")
            title = row.get("Title", "").strip()[:100]
            pathway = row.get("PathwayName", "").strip()
            if not doi:
                print(f"[{pmid}] X No DOI found, skipping...")
                logs.append({
                    "PMID": pmid,
                    "PathwayName": pathway,
                    "Filename": None,
                    "Downloaded": False,
                    "Reason": "No DOI"
                })
                continue
            safe_pathway = re.sub(r"[^\w\-_\. ]", "_", pathway) or f"article_{pmid}"
            filename = f"{safe_pathway}__{pmid}.pdf"
            output_path = os.path.join(OUTPUT_DIR, filename)
            print(f"\n[{pmid}]")
            print(f"    Titre       : {title}")
            print(f"    DOI         : {doi}")
            print(f"    Pathway     : {pathway}")
            print(f"    Fichier     : {filename}")
            if os.path.exists(output_path):
                print(f"Already download, skipping : {filename}")
                logs.append({
                    "PMID": pmid,
                    "PathwayName": pathway,
                    "Filename": filename,
                    "Downloaded": True,
                    "Reason": "Already exists"
                })
                continue
            print(f"Searching PDF for DOI : {doi}")
            pdf_url = try_all_scihub_mirrors(doi)
            if pdf_url:
                try:
                    print(f"Downloading PDF from {pdf_url}")
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                    }

                    pdf_response = requests.get(pdf_url, headers=headers, stream=True, timeout=20)
                    if pdf_response.status_code == 200:
                        with open(output_path, "wb") as f_out:
                            for chunk in pdf_response.iter_content(1024):
                                f_out.write(chunk)
                        print(f"PDF downloaded : {output_path}")
                        downloaded += 1
                        logs.append({
                            "PMID": pmid,
                            "PathwayName": pathway,
                            "Filename": filename,
                            "Downloaded": True,
                            "Reason": "Downloaded"
                        })
                    else:
                        print(f" X Unable to download the PDF (status {pdf_response.status_code})")
                        logs.append({
                            "PMID": pmid,
                            "PathwayName": pathway,
                            "Filename": filename,
                            "Downloaded": False,
                            "Reason": f"HTTP {pdf_response.status_code}"
                        })
                except Exception as e:
                    print(f" X Error : {e}")
                    logs.append({
                        "PMID": pmid,
                        "PathwayName": pathway,
                        "Filename": filename,
                        "Downloaded": False,
                        "Reason": f"Exception: {str(e)}"
                    })
            else:
                print(f" X PDF not found for DOI {doi} on Sci-Hub")
                logs.append({
                    "PMID": pmid,
                    "PathwayName": pathway,
                    "Filename": filename,
                    "Downloaded": False,
                    "Reason": "PDF not found on Sci-Hub"
                })
            time.sleep(1.5)
    print("Download done.")
    print(f"Processed articles : {total}")
    print(f"PDF downloaded : {downloaded}")
    print(f"PDF absent : {total - downloaded}")
    with open("log_downloads.json", "w", encoding="utf-8") as log_file:
        json.dump(logs, log_file, indent=2, ensure_ascii=False)
    print("Log saved in log_downloads.json")
if __name__ == "__main__":
    main()
