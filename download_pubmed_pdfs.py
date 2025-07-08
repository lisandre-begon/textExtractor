import os
import csv
import time
import requests
from bs4 import BeautifulSoup
import webbrowser

INPUT_FILE = "pubmed_articles.csv"
OUTPUT_DIR = "pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Miroirs Sci-Hub connus
SCI_HUB_MIRRORS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.hkvisa.net",
]

def try_scihub_url(scihub_url):
    print(f"  └─ Tentative d'accès à : {scihub_url}")
    try:
        response = requests.get(scihub_url, timeout=15)
        if response.status_code != 200:
            print(f"  ✘ Échec de chargement (status {response.status_code})")
            return False, None

        soup = BeautifulSoup(response.content, "html.parser")
        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            print(f"  ✘ Aucune iframe trouvée (pas de PDF visible)")
            return False, None

        pdf_url = iframe["src"]
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif pdf_url.startswith("/"):
            parts = scihub_url.split("/")
            pdf_url = parts[0] + "//" + parts[2] + pdf_url

        print(f"  ✔ Lien PDF trouvé : {pdf_url}")
        return True, pdf_url
    except Exception as e:
        print(f"  ✘ Erreur lors de l'accès à {scihub_url} → {e}")
        return False, None

def try_all_scihub_mirrors(doi):
    print(f"🔍 Recherche du PDF pour DOI: {doi}")
    for mirror in SCI_HUB_MIRRORS:
        scihub_url = f"{mirror}/{doi}"
        success, pdf_url = try_scihub_url(scihub_url)
        if success:
            print(f"✅ PDF localisé via {mirror}")
            return pdf_url
    print(f"❌ Aucun miroir Sci-Hub n'a permis d'accéder au PDF.")
    return None

def main():
    print("=== 📥 Lancement du téléchargement des PDF PubMed ===\n")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        total = 0
        downloaded = 0
        for row in reader:
            total += 1
            pmid = row.get("PMID")
            doi = row.get("DOI")
            title = row.get("Title", "").strip()[:100]
            if not doi:
                print(f"[{pmid}] ❌ Aucun DOI — article ignoré")
                continue

            filename = f"{pmid}.pdf"
            output_path = os.path.join(OUTPUT_DIR, filename)

            print(f"\n=== ▶️ Traitement de PMID {pmid} ===")
            print(f"    Titre : {title}")
            print(f"    DOI   : {doi}")

            if os.path.exists(output_path):
                print(f"    🟡 Déjà téléchargé : {filename}")
                continue

            print(f"    📡 Tentative de téléchargement du PDF...")
            pdf_url = try_all_scihub_mirrors(doi)

            if pdf_url:
                try:
                    print(f"    ⬇️ Téléchargement du fichier PDF...")
                    pdf_response = requests.get(pdf_url, stream=True, timeout=20)
                    if pdf_response.status_code == 200:
                        with open(output_path, "wb") as f_out:
                            for chunk in pdf_response.iter_content(1024):
                                f_out.write(chunk)
                        print(f"    ✅ PDF enregistré : {output_path}")
                        downloaded += 1
                    else:
                        print(f"    ❌ PDF non téléchargeable (status {pdf_response.status_code})")
                except Exception as e:
                    print(f"    ❌ Erreur pendant le téléchargement : {e}")
            else:
                fallback_url = f"https://sci-hub.se/{doi}"
                print(f"    🚪 Ouverture dans le navigateur : {fallback_url}")
                webbrowser.open(fallback_url)

            time.sleep(1.5)

    print("\n=== ✅ Terminé ===")
    print(f"Articles traités : {total}")
    print(f"PDF téléchargés  : {downloaded}")
    print(f"PDF manquants    : {total - downloaded}")

if __name__ == "__main__":
    main()
