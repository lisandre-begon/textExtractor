import re

text = "textFiles/file1_exemple.txt"

transformation_keywords = [
    "biodegradation", "degradation", "biotransformation", "transformation",
    "mineralization", "oxidation", "hydrolysis", "cleavage",
    "conversion", "depolymerization", "disappearance",
    "catabolism", "breakdown", "metabolized", "elimination"
]


result_keywords = [
    "DOC removal", "CO₂ evolution", "TOC removal", "respirometry",
    "mineralized", "metabolite", "intermediate", "product formation",
    "mass loss", "reduction", "removal efficiency", "depletion"
]

agent_keywords = [
    "enzyme", "microorganism", "bacteria", "fungi", "microbe",
    "activated sludge", "digested sludge", "consortium", "isolate",
    "biocatalyst", "cell culture", "inoculum", "biomass"
]

condition_keywords = [
    "aerobic", "anaerobic", "oxic", "anoxic", "temperature", "pH",
    "incubation", "test", "duration", "concentration", "conditions",
    "OECD", "ISO", "respirometric", "batch test"
]

methodology_keywords = [
    "assessed", "evaluated", "measured",
    "was tested", "was studied", "was examined", "was monitored",
    "was analyzed", "investigated"
]


keywords = {
    transformation_keywords + result_keywords + agent_keywords + condition_keywords + methodology_keywords
}

