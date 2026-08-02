#!/usr/bin/env python3
"""
Fix duplicate symptom lists - remove generic placeholder items.
"""
import re
from pathlib import Path

DISEASES_DIR = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/diseases")

PLACEHOLDER_ITEMS = [
    "Functional impairment affecting daily activities",
    "Changes in appearance or function of affected tissues",
    "Systemic symptoms may include fatigue, fever, or weight changes",
    "Symptoms may develop gradually or appear suddenly",
]

def fix_symptoms(content):
    """Remove generic placeholder items from symptom lists."""
    for item in PLACEHOLDER_ITEMS:
        # Remove the item line
        pattern = rf'\n  \\item {re.escape(item)}'
        content = re.sub(pattern, '', content)
        
        # Also clean up concatenated versions in first item
        pattern2 = rf'{re.escape(item)}\s+'
        content = re.sub(pattern2, ' ', content)
    
    return content

def main():
    fixed = 0
    for filepath in DISEASES_DIR.glob("*.tex"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content = fix_symptoms(content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath.name}")
            fixed += 1
    
    print(f"\nTotal files fixed: {fixed}")


if __name__ == "__main__":
    main()
