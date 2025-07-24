import subprocess
import sys

# Helper function to run a script and check result
def run_step(script_name, description):
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        if result.returncode == 0:
            print(f" {description} finished successfully.")
        else:
            print(f"ERROR: {description} failed with return code {result.returncode}.")
    except Exception as e:
        print(f"ERROR: Error running {description}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n Starting full PubMed → Sci-Hub → Direct Filtering pipeline...\n")

    # 1. Fetch PubMed metadata
    run_step("get_Pubmed_Article.py", "Step 1: Fetch PubMed metadata & create pubmed_articles.csv")

    # 2. Download PDFs + Directly Filter Text
    run_step("download_pubmed_pdfs.py", "Step 2: Download PDFs from Sci-Hub & Direct Filtering")

    print("\n Pipeline finished!")
    print("Results:")
    print("  • pubmed_articles.csv → metadata")
    print("  • pdfs/               → downloaded PDFs")
    print("  • filtered_sentences/ → final relevant text (no intermediate cleaning needed)")