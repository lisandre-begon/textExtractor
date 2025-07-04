import re
import csv 
import json
from Bio import Entrez

Entrez.email = "lisandre.begon1@gmail.com"

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


def fetch_pubmed_metadata(pmid):
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        records = Entrez.read(handle)
        article = records[0]["MedlineCitation"]["Article"]
        article_ids = records[0]["PubmedData"]["ArticleIdList"]

        title = article["ArticleTitle"]
        journal = article["Journal"]["Title"]
        authors = ", ".join(f"{a['LastName']} {a['Initials']}" for a in article.get("AuthorList", []))
        abstract = article.get("Abstract", {}).get("AbstractText", [""])[0]
        doi = next((x for x in article_ids if x.attributes["IdType"] == "doi"), "")

        return {
            "PMID": pmid,
            "Title": title,
            "Journal": journal,
            "Authors": authors,
            "Abstract": abstract,
            "DOI": doi,
            "SciHub": f"https://sci-hub.se/{doi}" if doi else ""
        }
    
    except Exception as e:
        return {"PMID": pmid, "Error": str(e)}

def main():
    pathway_entries = load_pathway_descriptions()

    results = []
    for entry in pathway_entries:
        pathway_name = entry["name"]
        pmids = extract_pubmed_ids(entry["description"])
        for pmid in pmids:
            metadata = fetch_pubmed_metadata(pmid)
            metadata["PathwayName"] = pathway_name
            results.append(metadata)

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
