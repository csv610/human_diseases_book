# All About Human Diseases: An Organ-Categorized Medical Reference

**Author:** Chaman Singh Verma  
**Document Format:** LaTeX / PDF (383 pages)  
**Total Coverage:** 31 Chapters | 199 Sections | 862 Subsections  

---

## 📖 Overview

*All About Human Diseases: An Organ-Categorized Medical Reference* is a comprehensive, high-yield medical reference catalog detailing **862 human diseases and disorders** across 31 organ systems and clinical specialties.

Every disease entry follows a standardized, evidence-based clinical architecture:
$$\text{Etiology} \longrightarrow \text{Pathophysiology} \longrightarrow \text{Clinical Features} \longrightarrow \text{Diagnostics} \longrightarrow \text{Management} \longrightarrow \text{Prognosis}$$

---

## 📂 Repository Structure

```
HumanDiseases/
├── chapters/              # 31 Organ System Chapter LaTeX files (.tex)
├── images/                # Clinical Figures & Image Assets
├── main.tex               # Master LaTeX Source Document
├── main.pdf               # Compiled Book PDF (383 pages)
├── frontpage.png          # High-Resolution Book Cover Art
└── README.md
```

---

## 🛠️ Building the PDF

To compile the book locally using `pdflatex`:

```bash
pdflatex -interaction=nonstopmode main.tex
makeindex main.idx
pdflatex -interaction=nonstopmode main.tex
```

---

## 📜 License

© 2026 Chaman Singh Verma. All rights reserved.
