#!/usr/bin/env python3
"""
Remove 4 broken appendix links to non-existent diseases.
"""
from pathlib import Path

APPENDIX_FILE = Path("/Users/csv610/Projects/MyBooks/HumanDiseases/appendix_organ_dictionary.tex")

BROKEN_LABELS = [
    "Ascariasis (Ascaris lumbricoides Infection)",
    "Behçet's Disease",
    "Ménière's Disease",
    "Sjögren's Syndrome",
]

def fix_appleix():
    content = APPENDIX_FILE.read_text(encoding='utf-8')
    lines = content.split('\n')
    fixed = []
    removed = 0
    
    for line in lines:
        skip = False
        for label in BROKEN_LABELS:
            if f'sec:{label}' in line:
                skip = True
                removed += 1
                break
        if not skip:
            fixed.append(line)
    
    APPENDIX_FILE.write_text('\n'.join(fixed), encoding='utf-8')
    print(f"Removed {removed} broken links")
    print(f"Remaining lines: {len(fixed)}")

if __name__ == "__main__":
    fix_appleix()
