import re 
import os


# Load the txt file, clean the lines and return with a format of text
#Input : path to the text file
#Output : list of lines without empty lines and format
def load_clean_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]
    
    format = detect_text_format(lines)
    return lines, format
    

# Detect the format of the text based on the content of the lines
#Input : list of lines without empty lines and comments
#Output : "empty", "short", "paragraph", "table" or "unknown"
def detect_text_format(lines):

    total_lines = len(lines)
    if total_lines == 0:
        return "empty"


    short_lines = [line for line in lines if len(line.split()) <= 5]
    # calculate average number of words per line
    avg_words = sum(len(line.split()) for line in lines) / total_lines
    punctuated_lines = [line for line in lines if re.search(r'[.;:]', line)]
    # check for lines with multiple spaces (indicating a table-like structure)
    table_like_lines = [line for line in lines if re.search(r'\s{2,}', line) and len(line.split()) >= 3]

    short_ratio = len(short_lines) / total_lines
    punct_ratio = len(punctuated_lines) / total_lines
    table_ratio = len(table_like_lines) / total_lines

    # check how diverse short lines are
    unique_short_lines = set(short_lines)
    uniqueness_ratio = len(unique_short_lines) / len(short_lines) if short_lines else 0

    # Field_value: many short lines, but mostly repeated headers (low uniqueness)
    if short_ratio > 0.4 and uniqueness_ratio < 0.7 and punct_ratio < 0.3:
        return "field_value"

    # Table: looks like aligned columns
    if table_ratio > 0.5:
        return "table_text"

    # Paragraph: enough punctuation and longer lines
    if punct_ratio > 0.3 or avg_words > 7:
        return "paragraph"

    return "unknown"
    
# Clean the text based on the detected format
#Input : list of lines without empty lines and comments
#Output : cleaned text based on the format
def clean_text(lines, mode):
    if mode == "paragraph":
        # Return a single cleaned paragraph string
        return " ".join(lines)

    elif mode == "field_value":
        # Return list of (key, value) tuples for raw field-value style documents
        pairs = []
        current_key = None
        for line in lines:
            if re.match(r"^[A-Za-z \-/]{2,}$", line) and len(line.split()) < 6:
                current_key = line
            elif current_key:
                pairs.append((current_key, line))
                current_key = None
        return pairs

    elif mode == "table_text":
        # Return list of column lists from tabular-looking text
        table = []
        for line in lines:
            columns = re.split(r'\s{2,}', line.strip())
            if len(columns) > 1:
                table.append(columns)
        return table

    else:
        # Unknown mode: return first lines as is
        return {
            "note": "Unknown format; raw preview returned.",
            "lines": lines[:5]
        }


def process_text_file(file_path, output_folder="./textFilesCleaned/"):
    # Load and clean lines from the file
    lines = load_clean_lines(file_path)
    
    # Detect the format of the text
    format = detect_text_format(lines)
    
    # Clean the text based on the detected format
    cleaned = clean_text(lines, format)
    
    if isinstance(cleaned, str):
        cleaned_text = cleaned

    elif isinstance(cleaned, list):
        if all(isinstance(item, tuple) and len(item) == 2 for item in cleaned):  # field_value
            cleaned_text = "\n".join(f"{k}: {v}" for k, v in cleaned)
        elif all(isinstance(item, list) for item in cleaned):  # table_text
            cleaned_text = "\n".join("\t".join(row) for row in cleaned)
        else:
            cleaned_text = "\n".join(map(str, cleaned))  # fallback

    else:
        cleaned_text = str(cleaned)

    filename = os.path.basename(file_path)
    output_path = os.path.join(output_folder, filename)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(cleaned_text)

    return {
        "mode": format,
        "output_path": output_path,
    }