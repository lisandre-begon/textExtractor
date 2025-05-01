from cleanTxt import process_text_file
import os

folder = "textFiles"

for file in os.listdir(folder):
    if file.endswith(".txt"):
        file_path = os.path.join(folder, file)
        print(f"Processing {file_path}...")
        result = process_text_file(file_path)
        print(f"Saved to: {result['output_path']}")
        print(f"Format detected: {result['mode']}\n")
