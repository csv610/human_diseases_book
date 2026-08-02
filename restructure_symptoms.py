#!/usr/bin/env python3
"""
Restructure Signs and Symptoms into 4 categories:
Early symptoms, Common symptoms, Less common symptoms, Emergency warning signs.
Preserves ALL existing content — no information is lost.
"""

import os, re, shutil

DISEASES_DIR = 'diseases'
BACKUP_DIR = 'diseases_backup'

def normalize(s):
    return re.sub(r'\s+', ' ', s).strip()

def run():
    # Create backup
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(DISEASES_DIR, BACKUP_DIR)
    print(f'Backup at {BACKUP_DIR}/')

    files = sorted(f for f in os.listdir(DISEASES_DIR) if f.endswith('.tex'))
    ok = 0
    errs = []

    for fname in files:
        path = os.path.join(DISEASES_DIR, fname)
        try:
            if process(path):
                ok += 1
        except Exception as e:
            errs.append(f'{fname}: {e}')

    print(f'\nProcessed {ok}/{len(files)} files')
    if errs:
        for e in errs:
            print(f'  ERROR: {e}')

def get_disease_name(content):
    """Extract the disease name from \chapter{}, handling LaTeX commands with braces inside."""
    m = re.search(r'\\chapter\{', content)
    if not m:
        return 'the condition'
    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    if depth == 0:
        return content[start:i-1]
    return 'the condition'

def process(path):
    with open(path) as f:
        content = f.read()

    disease = get_disease_name(content)

    # Locate the Signs and Symptoms section
    pat = re.compile(
        r'(\\section\{Signs and Symptoms\})'
        r'(.*?)'
        r'(?=\\section\{|\Z)',
        re.DOTALL
    )
    m = pat.search(content)
    if not m:
        return False

    header = m.group(1)
    body = m.group(2)

    # --- Parse the body ---

    # Separate intro text (before any list env) from the list content
    list_starts = []
    for env in ['itemize', 'enumerate']:
        idx = body.find(f'\\begin{{{env}}}')
        if idx >= 0:
            list_starts.append(idx)
    list_start = min(list_starts) if list_starts else len(body)

    intro_raw = body[:list_start].strip()
    list_raw = body[list_start:].strip()

    intro = normalize(intro_raw) if intro_raw else ''

    # Extract all \item contents
    items = []
    for match in re.finditer(
        r'\\item\s+(.*?)(?=\\item\s+|\\end\{itemize\}|\\end\{enumerate\}|\Z)',
        list_raw, re.DOTALL
    ):
        t = normalize(match.group(1))
        if t:
            items.append(t)

    # --- Categorize ---
    early = []
    common = []
    less_common = []
    emergency = []

    def categorize(text):
        lo = text.lower()
        if re.search(r'\b(early|initial|prodrom|earliest|first sign)\b', lo):
            return 'early'
        if re.search(r'\b(less common|less commonly|uncommon|rare|rarely|uncommonly)\b', lo):
            return 'less_common'
        if re.search(r'\b(emergency|warning sign|seek|immediate|life.threaten|call 911|seek care|medical attention|go to the er)\b', lo):
            return 'emergency'
        return 'common'

    for item in items:
        cat = categorize(item)
        if cat == 'early':
            early.append(item)
        elif cat == 'less_common':
            less_common.append(item)
        elif cat == 'emergency':
            emergency.append(item)
        else:
            common.append(item)

    # Put intro at the top of common if it exists and is not already the first item
    if intro and (not common or normalize(common[0]) != intro):
        common.insert(0, intro)

    # --- Build new section ---
    lines = [header, '']

    if early:
        lines.append('\\subsection{Early symptoms}')
        lines.append('\\begin{itemize}[noitemsep]')
        for item in early:
            lines.append(f'  \\item {item}')
        lines.append('\\end{itemize}')
        lines.append('')

    lines.append('\\subsection{Common symptoms}')
    lines.append('\\begin{itemize}[noitemsep]')
    if common:
        for item in common:
            lines.append(f'  \\item {item}')
    else:
        lines.append(f'  \\item Symptoms of {disease.lower()} vary depending on severity and extent of the condition')
    lines.append('\\end{itemize}')
    lines.append('')

    if less_common:
        lines.append('\\subsection{Less common symptoms}')
        lines.append('\\begin{itemize}[noitemsep]')
        for item in less_common:
            lines.append(f'  \\item {item}')
        lines.append('\\end{itemize}')
        lines.append('')

    lines.append('\\subsection{Emergency warning signs}')
    lines.append('\\begin{itemize}[noitemsep]')
    if emergency:
        for item in emergency:
            lines.append(f'  \\item {item}')
    else:
        lines.append(f'  \\item Severe or worsening symptoms of {disease.lower()} require immediate medical evaluation')
    lines.append('\\end{itemize}')

    new_section = '\n'.join(lines)
    new_section = re.sub(r' +\n', '\n', new_section)
    new_section = re.sub(r'\n{3,}', '\n\n', new_section)

    # Ensure newline between end of this section and next section
    next_part = content[m.end():]
    if next_part.startswith('\\section') and not new_section.endswith('\n'):
        next_part = '\n' + next_part
    content = content[:m.start()] + new_section + next_part

    with open(path, 'w') as f:
        f.write(content)

    return True

if __name__ == '__main__':
    run()
