import re

def split_text_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())

def build_abbreviation_dict(text):
    """
    Scan the text and build a mapping:
    ABBREV -> full compound name
    
    Example:
      "1,1,1-trichloroethane (TCA)" 
         -> mapping["TCA"] = "1,1,1-trichloroethane"
    """
    mapping = {}
    
    # Regex for patterns: full name (ABBR)
    # full name: letters, numbers, commas, dashes, spaces
    # abbreviation: 2-6 uppercase letters/numbers
    pattern = r'([A-Za-z,\-\s0-9]+?)\s*\(([A-Z]{2,6})\)'
    
    for full, abbr in re.findall(pattern, text):
        # Clean inputs
        full_clean = full.strip().lower()
        abbr_clean = abbr.strip().upper()

        # Filter out garbage
        if len(abbr_clean) < 2 or len(abbr_clean) > 6:
            continue  # too short/long
        if abbr_clean.isdigit():
            continue  # year or number
        if len(full_clean.split()) < 1:
            continue  # too short
        mapping[abbr_clean] = full_clean
    return mapping

def normalize_compounds(compounds, mapping):
    normalized = []
    for c in compounds:
        if c in mapping:
            normalized.append(mapping[c])  # replace TCA -> full name
        else:
            normalized.append(c.lower())  # fallback to lowercase
    return normalized

def process_text_group_sentences(text):

    """
    Main function:
    - Keeps only relevant sentences
    - Groups logically (adds blank lines when subject changes)
    """

    sentences = split_text_into_sentences(text)

    # --- Context memory ---
    context = {
            "current_parent": None,
            "current_compounds": [],
            "previous_block_compounds": []
    }

    results = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # --- Extract all signals ---
        raw_compounds = extract_compounds(sentence)
        compounds = normalize_compounds(raw_compounds, mapping)
        reaction = extract_reaction(sentence)
        numeric_info = extract_numeric(sentence)
        condition = extract_conditions(sentence)

        # Is this sentence relevant? 
        if not (compounds or reaction or numeric_info or condition):
            continue  # skip irrelevant

        # --- Update context ---
        if compounds:
            # If it's a reaction, update the parent
            if reaction and reaction["from"]:
                context["current_parent"] = reaction["from"]

            # Update current compounds
            context["current_compounds"] = compounds

        # --- Decide if we need a blank line (new block) ---
        # If compounds are present AND there is no overlap with the last block, new subject
        if compounds:
            if not set(compounds).intersection(set(context["previous_block_compounds"])):
                if results and results[-1] != "":
                    results.append("")  # blank line before starting new block
                context["previous_block_compounds"] = compounds

        # If no compounds but numeric/condition → stays in same block

        # --- Append this sentence ---
        results.append(sentence)

    return results



if __name__ == "__main__":
    # Example usage
    textpath = "clean_pdfs/1_5-Anhydro-D-fructose _Fungal___15110094.txt"

    with open(textpath, "r", encoding="utf-8") as file:
        text = file.read()

    mapping = build_abbreviation_dict(text)
    print("Abbreviation mapping:", mapping)

