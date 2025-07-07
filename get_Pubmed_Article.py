import re
import csv 
import json
from Bio import Entrez
import time
import xml.etree.ElementTree as ET

Entrez.email = "lisandre.begon1@gmail.com"
Entrez.api_key = "44f17efcba4e206d6cfa2e05a38c3932d009"

def load_pathway_descriptions(json_file="envipathData/bbd.json"):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pathway_entries = []
    for pathway in data.get('pathways', []):
        desc = pathway.get('description', '')
        name = pathway.get('name', '')
        if desc:
            pathway_entries.append({"name": name, "description": desc})
    return pathway_entries

def extract_pubmed_ids(text):
    return re.findall(r'(?:pubmed\.ncbi\.nlm\.nih\.gov|www\.ncbi\.nlm\.nih\.gov/pubmed)/(\d+)', text)

def fetch_pubmed_metadata(pmid, pathway_name=""):
    try:
        with Entrez.efetch(db="pubmed", id=pmid, retmode="xml") as handle:
            xml_content = handle.read()
        
        root = ET.fromstring(xml_content)
        article = root.find(".//PubmedArticle/MedlineCitation/Article")

        title = article.findtext("ArticleTitle", "")
        journal = article.findtext("Journal/Title", "")
        abstract_elem = article.find("Abstract/AbstractText")
        abstract = abstract_elem.text if abstract_elem is not None else ""
        authors_list = article.findall("AuthorList/Author")
        authors = ", ".join(f"{a.findtext('LastName', '')} {a.findtext('Initials', '')}".strip() for a in authors_list if a.find("LastName") is not None)

        # Extract DOI from the ArticleIdList
        doi = ""
        for id_elem in root.findall(".//ArticleIdList/ArticleId"):
            if id_elem.attrib.get("IdType") == "doi":
                doi = id_elem.text
                break

        return {
            "PMID": pmid,
            "Title": title,
            "Journal": journal,
            "Authors": authors,
            "Abstract": abstract,
            "DOI": doi,
            "PubMedURL": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}",
            "SciHub": f"https://sci-hub.se/{doi}" if doi else "",
            "PathwayName": pathway_name
        }

    except Exception as e:
        return {
            "PMID": pmid,
            "Error": str(e),
            "PathwayName": pathway_name
        }


def main():
    pathway_entries = load_pathway_descriptions()

    results = []
    for entry in pathway_entries:
        pathway_name = entry["name"]
        pmids = extract_pubmed_ids(entry["description"])
        for pmid in pmids:
            metadata = fetch_pubmed_metadata(pmid)
            metadata["PathwayName"] = pathway_name
            print(f"Fetched: {metadata}")
            results.append(metadata)
            time.sleep(0.5)

    if results:
        with open("pubmed_articles.csv", "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f" Saved {len(results)} articles to pubmed_articles.csv")
    else:
        print(" No PubMed articles found in the pathway descriptions.")

if __name__ == "__main__":
    main()
