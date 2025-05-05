from cleanTxt import process_text_file
from dotenv import load_dotenv
import os

load_dotenv()

folder = os.getenv("TEXT_FILES")

for file in os.listdir(folder):
    if file.endswith(".txt"):
        file_path = os.path.join(folder, file)
        print(f"Processing {file_path}...")
        result = process_text_file(file_path, output_folder=os.getenv("TEXT_FILES_CLEANED"))
        print(f"Saved to: {result['output_path']}")
        print(f"Format detected: {result['mode']}\n")
