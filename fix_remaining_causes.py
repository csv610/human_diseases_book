#!/usr/bin/env python3
"""
Fix the 3 remaining diseases with empty/generic Causes sections.
"""
import re
from pathlib import Path

DISEASES_DIR = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/diseases")

DISEASE_FIXES = {
    "Achalasia.tex": "This condition results from progressive degeneration of inhibitory nitrergic ganglion cells in the myenteric (Auerbach) plexus of the esophageal wall, leading to impaired lower esophageal sphincter relaxation.",
    "Abnormal_Uterine_Bleeding.tex": "This condition arises from structural abnormalities (POLM-COEIN classification: Polyps, Ovulatory dysfunction, Leiomyoma, Malignancy, Coagulopathy), endometrial dysfunction, or iatrogenic causes including hormonal contraception.",
    "Occipital_Neuralgia.tex": "This condition is caused by irritation or compression of the occipital nerves (greater, lesser, or third occipital), often due to cervical spine pathology, trauma, muscle tension, or compression by adjacent structures.",
    "Vitamin_B12_Cobalamin_Deficiency.tex": "This condition results from inadequate dietary intake (strict veganism), malabsorption (pernicious anemia, gastrectomy, ileal resection, bacterial overgrowth), or medications (metformin, proton pump inhibitors).",
    "Vitamin_C_Deficiency_Scurvy.tex": "This condition is caused by severe dietary deficiency of vitamin C (ascorbic acid), leading to impaired collagen synthesis, defective capillary integrity, and compromised wound healing.",
}

def fix_causes(filepath, fix_text):
    """Replace empty or generic Causes section with specific content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern for empty Causes section
    empty_pattern = r'(\\section\{Causes\}\n)(\\section\{Risk Factors\})'
    replacement = f'\\1{fix_text}\\n\\2'
    
    # Pattern for Causes with generic text
    generic_pattern = r'(\\section\{Causes\}\n)(.*?)(\n\n\\section)'
    
    def clean_generic(match):
        causes_text = match.group(2).strip()
        # If it contains generic phrases, replace
        if "underlying mechanisms" in causes_text.lower() or "complex interactions" in causes_text.lower():
            next_section = match.group(3)
            return match.group(1) + fix_text + "\n" + next_section
        return match.group(0)
    
    # Try empty pattern first
    if re.search(empty_pattern, content):
        content = re.sub(empty_pattern, replacement, content)
    else:
        # Try generic pattern
        content = re.sub(generic_pattern, clean_generic, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed: {filepath.name}")


def main():
    for filename, fix_text in DISEASE_FIXES.items():
        filepath = DISEASES_DIR / filename
        if filepath.exists():
            fix_causes(filepath, fix_text)
        else:
            print(f"NOT FOUND: {filename}")
    
    # Also fix Achondroplasia trailing generic
    filepath = DISEASES_DIR / "Achondroplasia.tex"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove trailing generic text
        content = re.sub(r'\s+The underlying mechanisms involve complex interactions.*', '', content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: Achondroplasia.tex (trailing text)")


if __name__ == "__main__":
    main()
