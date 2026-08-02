#!/usr/bin/env python3
"""
Fix template/bucket text in disease chapter files.
Removes generic placeholder text and duplicate symptom lists.
"""
import os
import re
from pathlib import Path

DISEASES_DIR = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/diseases")

# Generic template phrases to remove from Overview sections
TEMPLATE_PHRASES = [
    r"This condition affects a significant number of people worldwide",
    r"and can range from mild to severe in presentation\.",
    r"Early recognition and appropriate management are essential for optimal outcomes\.",
    r"A thorough understanding of the underlying mechanisms guides treatment decisions\.",
    r"Patient education and self-management play important roles in long-term care\.",
    r"Prompt diagnosis and appropriate management are essential for optimal outcomes\.",
    r"Prompt medical intervention is critical for optimal outcomes\.",
    r"Early recognition and appropriate management are essential for optimal outcomes\.",
]

# Generic "symptoms vary" sentence that's duplicated
SYMPTOMS_VARY = r"Symptoms vary depending on the severity and extent of the condition"

# Generic placeholder items that appear in all entries
PLACEHOLDER_ITEMS = [
    r"Functional impairment affecting daily activities",
    r"Changes in appearance or function of affected tissues",
    r"Systemic symptoms may include fatigue, fever, or weight changes",
    r"Symptoms may develop gradually or appear suddenly",
]


def clean_overview(text):
    """Remove generic template phrases from Overview section."""
    for phrase in TEMPLATE_PHRASES:
        text = re.sub(phrase, "", text)
    # Clean up double periods and extra spaces
    text = re.sub(r"\.\s*\.", ".", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def clean_symptoms_list(text):
    """Fix the duplicate symptoms list pattern."""
    # Pattern: first item has all symptoms concatenated, then each symptom as separate item
    # Remove the generic placeholder items
    for item in PLACEHOLDER_ITEMS:
        text = re.sub(rf'\\item\s*{item}\s*', '', text)
    return text


def clean_risk_factors(text):
    """Clean up Risk Factors section - remove concatenated list before itemize."""
    # Look for a paragraph of concatenated risk factors before itemize
    # Pattern: text ending with newlines, then \begin{itemize}
    pattern = r'(\\section\{Risk Factors\}[^\n]*\n)([^\n]+(?:\n[^\n]+)*?)(\n\n\\begin\{itemize\})'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        section = match.group(1)
        bullet_text = match.group(2)
        itemize_start = match.group(3)
        
        # Check if bullet_text is mostly generic/non-disease-specific
        # If it contains specific disease info, keep it; otherwise remove it
        lines = [l.strip() for l in bullet_text.strip().split('\n') if l.strip()]
        # If all lines are generic or there's only one concatenated line, remove it
        if len(lines) <= 1 or all(' ' in line and not any(c.isupper() for c in line[:10]) for line in lines):
            text = text[:match.start()] + section + itemize_start + text[match.end():]
    
    return text


def process_file(filepath):
    """Process a single disease file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Clean Overview section
    overview_pattern = r'(\\section\{Overview\}[^\n]*\n)([^\n]*\.?[^\n]*\.?[^\n]*\.?)'
    match = re.search(overview_pattern, content, re.DOTALL)
    if match:
        section_header = match.group(1)
        section_content = match.group(2)
        cleaned = clean_overview(section_content)
        content = content[:match.start()] + section_header + cleaned + content[match.end():]
    
    # Clean symptoms lists
    content = clean_symptoms_list(content)
    
    # Clean risk factors
    content = clean_risk_factors(content)
    
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
