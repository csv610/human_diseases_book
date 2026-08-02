#!/usr/bin/env python3
"""
Fix broken appendix hyperlinks by matching to actual disease file labels.
"""
import re
from pathlib import Path

APPENDIX_FILE = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/appendix_organ_dictionary.tex")
DISEASES_DIR = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/diseases")

def get_existing_labels():
    """Get all valid disease labels from disease files."""
    labels = {}
    for filepath in DISEASES_DIR.glob("*.tex"):
        content = filepath.read_text(encoding='utf-8')
        match = re.search(r'\\label\{sec:([^}]+)\}', content)
        if match:
            labels[match.group(1)] = filepath.name
    return labels

def get_appleix_links():
    """Get all hyperlink labels from appendix."""
    content = APPENDIX_FILE.read_text(encoding='utf-8')
    pattern = r'\\hyperlink\{sec:([^}]+)\}'
    return re.findall(pattern, content)

def fix_links():
    """Fix broken hyperlinks in appendix."""
    existing = get_existing_labels()
    appendix_links = get_appleix_links()
    
    # Create mapping of similar names
    fixes = {}
    for link in appendix_links:
        if link not in existing:
            # Try to find a match
            for existing_label in existing:
                # Check if they're similar (remove spaces, compare)
                if link.replace(' ', '').lower() == existing_label.replace(' ', '').lower():
                    fixes[link] = existing_label
                    break
                # Check if one contains the other
                elif link.lower() in existing_label.lower() or existing_label.lower() in link.lower():
                    fixes[link] = existing_label
                    break
    
    # Apply fixes
    content = APPENDIX_FILE.read_text(encoding='utf-8')
    for old, new in fixes.items():
        content = content.replace(f'hyperlink{{{old}}}', f'hyperlink{{{new}}}')
        print(f"Fixed: {old} -> {new}")
    
    APPENDIX_FILE.write_text(content, encoding='utf-8')
    print(f"\nTotal fixes: {len(fixes)}")

if __name__ == "__main__":
    fix_links()
