#!/usr/bin/env python3
"""
Fix generic Causes sections and duplicate symptom lists in disease chapters.
"""
import os
import re
from pathlib import Path

DISEASES_DIR = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/diseases")

# Generic template phrases to remove from Causes
GENERIC_CAUSES_PHRASES = [
    r"The underlying mechanisms involve complex interactions between genetic predisposition and environmental factors\.",
    r"Disruption of normal physiological processes leads to the characteristic features of the condition\.",
    r"Multiple contributing factors may act synergistically to trigger or worsen the condition\.",
    r"Understanding the specific cause helps guide targeted treatment approaches\.",
    r"Genetic mutations account for some conditions, while others are sporadic or environmentally triggered\.",
    r"Protein aggregation and accumulation is a common mechanism in many disorders\.",
    r"Excitotoxicity, oxidative stress, and neuroinflammation contribute to neuronal injury\.",
    r"Neurological disorders involve dysfunction of neurons, glial cells, or neural circuits\.",
    r"The underlying mechanisms may include protein aggregation, neurotransmitter imbalances, demyelination, or structural abnormalities\.",
    r"Neurological dysfunction can result from structural abnormalities, neurodegenerative processes, demyelination, vascular injury, or neurotransmitter imbalances\.",
]

# Generic placeholder items to remove from symptom lists
PLACEHOLDER_ITEMS = [
    r"Functional impairment affecting daily activities",
    r"Changes in appearance or function of affected tissues",
    r"Systemic symptoms may include fatigue, fever, or weight changes",
    r"Symptoms may develop gradually or appear suddenly",
]


def clean_causes(content, disease_name):
    """Remove generic template text from Causes section."""
    # Pattern: \section{Causes} followed by generic text
    pattern = r'(\\section\{Causes\}[^\n]*\n)([^\n]+(?:\n[^\n]+)*?)(\n\n\\section|\\end\{document\})'
    
    def replace_causes(match):
        section = match.group(1)
        causes_text = match.group(2)
        next_section = match.group(3)
        
        # Check if causes_text contains specific disease info
        has_specific = any(phrase.lower() in causes_text.lower() for phrase in [
            disease_name.lower(),
            "virus", "bacteria", "infection", "mutation", "gene",
            "autoimmune", "tumor", "cancer", "deficiency",
        ])
        
        if not has_specific:
            # Replace with concise statement
            return section + f"This condition results from disruption of normal {disease_name.lower()} function.\n" + next_section
        else:
            # Clean up generic phrases
            for phrase in GENERIC_CAUSES_PHRASES:
                causes_text = re.sub(phrase, "", causes_text)
            causes_text = re.sub(r"\.\s*\.", ".", causes_text)
            causes_text = re.sub(r"\s{2,}", " ", causes_text).strip()
            return section + causes_text + "\n" + next_section
    
    return re.sub(pattern, replace_causes, content, flags=re.DOTALL)


def clean_symptoms(content):
    """Fix duplicate symptom lists."""
    # Pattern: first item has all symptoms concatenated, then generic placeholder items
    pattern = r'(\\subsection\{Common symptoms\}[^\n]*\n\\begin\{itemize\}[^\n]*\n)(  \\item [^\n]+)(\n  \\item Pain or discomfort)'
    
    def fix_symptoms(match):
        header = match.group(1)
        first_item = match.group(2)
        remaining = match.group(3)
        
        # Extract specific symptoms from first item (before "Symptoms may develop")
        specific = first_item.split("Symptoms may develop")[0].strip()
        specific = re.sub(r"Symptoms vary depending on the severity.*?(?=\s+(?:Pain|Functional|Changes|Systemic))", "", specific)
        specific = re.sub(r"\s+", " ", specific).strip()
        
        return header + f"  \\item {specific}\n" + remaining
    
    content = re.sub(pattern, fix_symptoms, content)
    
    # Remove generic placeholder items
    for item in PLACEHOLDER_ITEMS:
        content = re.sub(rf'\n  \\item {item}\s*', '', content)
    
    return content


def process_file(filepath):
    """Process a single disease file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Extract disease name from chapter
    match = re.search(r'\\chapter\{([^}]+)\}', content)
    disease_name = match.group(1) if match else "condition"
    
    # Clean causes
    content = clean_causes(content, disease_name)
    
    # Clean symptoms
    content = clean_symptoms(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    fixed = 0
    for filepath in DISEASES_DIR.glob("*.tex"):
        if process_file(filepath):
            print(f"Fixed: {filepath.name}")
            fixed += 1
    
    print(f"\nTotal files fixed: {fixed}")


if __name__ == "__main__":
    main()
