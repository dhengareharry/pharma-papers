# src/pharma_papers/fetch_papers.py
from typing import List, Dict, Optional
from Bio import Entrez
import csv
import logging

Entrez.email = "dhengareharry@gmail.com"  # Your email

def fetch_papers(query: str, debug: bool = False) -> List[Dict[str, str]]:
    """Fetch papers from PubMed and filter for pharma/biotech affiliations."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=10)
        record = Entrez.read(handle)
        ids = record["IdList"]
        logging.debug(f"Found {len(ids)} papers for query: {query}")
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return []
    
    results = []
    for pubmed_id in ids:
        paper_data = process_paper(pubmed_id, debug)
        if paper_data:
            results.append(paper_data)
    
    return results

def process_paper(pubmed_id: str, debug: bool) -> Optional[Dict[str, str]]:
    """Process a single paper and extract required fields."""
    try:
        handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
        record = Entrez.read(handle)
        article = record["PubmedArticle"][0]["MedlineCitation"]["Article"]
        
        title = article.get("ArticleTitle", "N/A")
        pub_date = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        pub_date_str = f"{pub_date.get('Year', 'N/A')}-{pub_date.get('Month', 'N/A')}"
        
        authors = article.get("AuthorList", [])
        non_academic_authors = []
        company_affiliations = []
        email = "N/A"
        
        for author in authors:
            affiliation = author.get("AffiliationInfo", [{}])[0].get("Affiliation", "")
            name = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
            
            if any(kw in affiliation.lower() for kw in ["pharma", "biotech", "company", "inc", "ltd"]):
                non_academic_authors.append(name)
                company_affiliations.append(affiliation)
            
            if author.get("AffiliationInfo") and "Email" in author["AffiliationInfo"][0]:
                email = author["AffiliationInfo"][0]["Email"]
        
        if non_academic_authors:
            return {
                "PubmedID": pubmed_id,
                "Title": title,
                "Publication Date": pub_date_str,
                "Non-academic Author(s)": "; ".join(non_academic_authors),
                "Company Affiliation(s)": "; ".join(company_affiliations),
                "Corresponding Author Email": email
            }
        return None
    except Exception as e:
        logging.debug(f"Error processing {pubmed_id}: {e}")
        return None

def save_to_csv(results: List[Dict[str, str]], filename: str) -> None:
    """Save results to a CSV file."""
    if not results:
        print("No results to save.")
        return
    
    keys = results[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filename}")