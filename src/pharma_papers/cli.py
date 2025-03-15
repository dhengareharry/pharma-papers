# src/pharma_papers/cli.py
import argparse
from pharma_papers.fetch_papers import fetch_papers, save_to_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with pharma/biotech affiliations.")
    parser.add_argument("query", help="PubMed search query")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--file", help="Output CSV filename")
    
    args = parser.parse_args()
    
    results = fetch_papers(args.query, args.debug)
    
    if args.file:
        save_to_csv(results, args.file)
    else:
        for result in results:
            print(result)

if __name__ == "__main__":
    main()