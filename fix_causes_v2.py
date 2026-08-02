#!/usr/bin/env python3
"""
Fix remaining generic Causes sections.
"""
import re
from pathlib import Path

DISEASES_DIR = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/diseases")

# Exact generic text patterns to remove
GENERIC_PHRASES = [
    "The underlying mechanisms involve complex interactions between genetic predisposition and environmental factors that disrupt normal physiological processes.",
    "The underlying mechanisms involve complex interactions between genetic predisposition and environmental factors.",
    "Disruption of normal physiological processes leads to the characteristic features of the condition.",
    "Multiple contributing factors may act synergistically to trigger or worsen the condition.",
    "Understanding the specific cause helps guide targeted treatment approaches.",
    "Genetic mutations account for some conditions, while others are sporadic or environmentally triggered.",
    "Protein aggregation and accumulation is a common mechanism in many disorders.",
    "Excitotoxicity, oxidative stress, and neuroinflammation contribute to neuronal injury.",
    "Neurological disorders involve dysfunction of neurons, glial cells, or neural circuits.",
    "The underlying mechanisms may include protein aggregation, neurotransmitter imbalances, demyelination, or structural abnormalities.",
    "Neurological dysfunction can result from structural abnormalities, neurodegenerative processes, demyelination, vascular injury, or neurotransmitter imbalances.",
]

def clean_causes(content, disease_name):
    """Remove generic template text from Causes section."""
    # Find Causes section
    causes_match = re.search(r'(\\section\{Causes\}[^\n]*\n)(.*?)(\n\n\\section|\n\n\\begin|\n\n\\end\{document\})', content, re.DOTALL)
    
    if not causes_match:
        return content
    
    section_start = causes_match.group(1)
    causes_text = causes_match.group(2)
    separator = causes_match.group(3)
    
    # Remove generic phrases
    for phrase in GENERIC_PHRASES:
        causes_text = causes_text.replace(phrase, "")
    
    # Clean up
    causes_text = re.sub(r'\n{2,}', '\n', causes_text)
    causes_text = causes_text.strip()
    
    # If causes_text is now empty or just generic, add a concise statement
    if not causes_text or len(causes_text) < 10:
        causes_text = f"This condition results from disruption of normal {disease_name.lower()} function."
    
    return content[:causes_match.start()] + section_start + causes_text + separator + content[causes_match.end():]


def main():
    fixed = 0
    for filepath in DISEASES_DIR.glob("*.tex"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract disease name
        match = re.search(r'\\chapter\{([^}]+)\}', content)
        disease_name = match.group(1) if match else "condition"
        
        original = content
        content = clean_causes(content, disease_name)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath.name}")
            fixed += 1
    
    print(f"\nTotal files fixed: {fixed}")


if __name__ == "__main__":
    main()
