#!/usr/bin/env python3
"""
Add Classification section to all disease chapters.
12 categories: Cause, Organ, Pathophysiology, Duration, Onset, Mode of Transmission,
Clinical Course, Severity, Extent of Disease, Age Group, Epidemiology, ICD-11
"""

import os, re, json
from pathlib import Path

DISEASES_DIR = Path('diseases')
files = sorted(f for f in DISEASES_DIR.iterdir() if f.suffix == '.tex')

# ============================================================
# CLASSIFICATION KNOWLEDGE BASE
# ============================================================

# Disease name -> classification overrides (specific knowledge)
SPECIFIC_CLASSIFICATIONS = {
    'abnormal uterine bleeding': {
        'cause': 'Hormonal imbalance, structural (polyps, fibroids, adenomyosis), coagulopathy, iatrogenic',
        'organ': 'Uterus, endometrium',
        'pathophysiology': 'Disrupted endometrial shedding due to hormonal dysregulation or structural lesions',
        'duration': 'Acute to chronic (months to years)',
        'onset': 'Perimenarchal to perimenopausal',
        'transmission': 'Non-communicable',
        'course': 'Recurrent, cyclic with menses',
        'severity': 'Mild to severe (anemia, quality of life impact)',
        'extent': 'Local (uterine cavity)',
        'age_group': 'Reproductive age (15-50 years)',
        'epidemiology': '10-30% of reproductive-age women; leading cause of gynecologic visits',
        'icd11': 'GA20.0 Abnormal uterine bleeding'
    },
    'abscess': {
        'cause': 'Bacterial infection (S. aureus, anaerobes, polymicrobial)',
        'organ': 'Skin, subcutaneous tissue, any organ',
        'pathophysiology': 'Localized collection of pus from tissue necrosis and neutrophilic infiltration',
        'duration': 'Acute (days to weeks)',
        'onset': 'Sudden to subacute',
        'transmission': 'Non-communicable (secondary to infection)',
        'course': 'Progressive without drainage; resolves with incision & antibiotics',
        'severity': 'Mild to life-threatening (sepsis)',
        'extent': 'Localized or deep',
        'age_group': 'All ages',
        'epidemiology': 'Common; skin abscesses increasing with MRSA',
        'icd11': 'LB50.0 Abscess'
    },
    'acne vulgaris': {
        'cause': 'Follicular hyperkeratinization, sebum overproduction, C. acnes, inflammation',
        'organ': 'Skin (pilosebaceous units: face, chest, back)',
        'pathophysiology': 'Androgen-driven sebum production + follicular plugging + bacterial colonization + immune response',
        'duration': 'Chronic (years, often adolescence to 20s)',
        'onset': 'Puberty (10-14 years)',
        'transmission': 'Non-communicable',
        'course': 'Relapsing-remitting; improves with age',
        'severity': 'Mild (comedonal) to severe (nodulocystic, scarring)',
        'extent': 'Localized (face, trunk) to generalized',
        'age_group': 'Adolescents (85%), young adults',
        'epidemiology': '85% of teens; 40-50% of adults 20-40',
        'icd11': 'ED10.0 Acne vulgaris'
    },
    'acute myocardial infarction': {
        'cause': 'Atherothrombotic coronary occlusion (plaque rupture + thrombus)',
        'organ': 'Heart (myocardium)',
        'pathophysiology': 'Coronary occlusion -> ischemia -> necrosis (20-40 min); wavefront progression',
        'duration': 'Acute (hours to days); healing 6-8 weeks',
        'onset': 'Sudden (often at rest or exertion)',
        'transmission': 'Non-communicable',
        'course': 'Acute event -> healing -> remodeling; risk of recurrence',
        'severity': 'Life-threatening (cardiogenic shock, arrhythmia, death)',
        'extent': 'Focal (STEMI) or diffuse (NSTEMI)',
        'age_group': '>45 years (men), >55 years (women)',
        'epidemiology': 'Leading cause of death globally; ~800k US/year',
        'icd11': 'BA41.0 Acute myocardial infarction'
    },
    'alzheimer disease': {
        'cause': 'Amyloid-beta plaques + tau neurofibrillary tangles; genetic (APOE4, APP, PSEN1/2)',
        'organ': 'Brain (hippocampus, cortex)',
        'pathophysiology': 'Amyloid cascade -> tau hyperphosphorylation -> synaptic loss -> neuronal death -> atrophy',
        'duration': 'Chronic progressive (8-10 years avg)',
        'onset': 'Insidious (>65 late-onset; <65 early-onset)',
        'transmission': 'Non-communicable',
        'course': 'Slowly progressive cognitive decline',
        'severity': 'Mild to severe (total dependence)',
        'extent': 'Diffuse cortical (temporal, parietal, frontal)',
        'age_group': '>65 years (95%); early-onset <65',
        'epidemiology': '6.7M US (2023); 55M global; doubling every 20 years',
        'icd11': '8A20 Alzheimer disease'
    },
    # Add more specific entries as needed
}

# ============================================================
# CLASSIFICATION RULES BY KEYWORDS
# ============================================================

CAUSE_RULES = [
    (r'\b(autoimmune|immune.*attack|antibod)', 'Autoimmune'),
    (r'\b(genetic|hereditary|mutation|gene|chromosome|trisomy)', 'Genetic'),
    (r'\b(congenital|birth defect|born with)', 'Congenital'),
    (r'\b(infect|bacteri|viral|fungal|parasit|prion|tubercul)', 'Infectious'),
    (r'\b(cancer|carcinoma|tumor|neoplasm|malignan|leukemia|lymphoma|melanoma|sarcoma)', 'Neoplastic'),
    (r'\b(metabolic|diabetes|thyroid|hormone|endocrine)', 'Metabolic/Endocrine'),
    (r'\b(nutrition|deficiency|vitamin|mineral|malnutrition)', 'Nutritional'),
    (r'\b(degenerat|aging|wear|tear|aging)', 'Degenerative'),
    (r'\b(toxic|poison|overdose|poisoning|exposure)', 'Toxic/Environmental'),
    (r'\b(drug|medication|iatrogenic)', 'Drug-induced/Iatrogenic'),
    (r'\b(trauma|injury|fracture|burn|accident)', 'Traumatic'),
    (r'\b(autoimmune|immune)', 'Autoimmune'),
    (r'\b(psych|mental|depress|anxiety|schizophren|bipolar)', 'Psychiatric'),
    (r'\b(vascular|stroke|ischemia|thrombosis|emboli)', 'Vascular'),
    (r'\b(autoimmune|immune)', 'Autoimmune'),
]

ORGAN_RULES = [
    (r'\b(heart|cardiac|cardio|myocardial|coronary|valve|arrhythmia|atrial|ventricular)', 'Heart'),
    (r'\b(lung|pulmonary|respiratory|bronchi|asthma|copd|pneumonia|pleural)', 'Lungs'),
    (r'\b(brain|neuro|cerebral|spinal|mening|encephal|seizure|epilepsy|stroke|dementia|alzheimer|parkinson)', 'Brain/Nervous System'),
    (r'\b(liver|hepatic|hepatitis|cirrhosis|hepatocellular)', 'Liver'),
    (r'\b(kidney|renal|nephro|dialysis|uremia)', 'Kidneys'),
    (r'\b(stomach|gastric|intestin|colon|rectal|bowel|cecal|appendic|diverticul|ibs|crohn|ulcerative)', 'Gastrointestinal'),
    (r'\b(skin|dermat|acne|psoriasis|eczema|melanoma|basal cell|squamous)', 'Skin'),
    (r'\b(blood|leukemia|lymphoma|anemia|hemophilia|thrombocytopenia|coagul)', 'Hematologic'),
    (r'\b(bone|joint|arthrit|osteo|muscle|muscular|skeletal|fracture|osteoporosis)', 'Musculoskeletal'),
    (r'\b(eye|retina|glaucoma|cataract|macular|vision|ophthalm)', 'Eyes'),
    (r'\b(ear|hearing|deaf|vertigo|tinnitus|otic)', 'Ears'),
    (r'\b(thyroid|parathyroid|adrenal|pituitary|endocrine|diabetes)', 'Endocrine'),
    (r'\b(uterus|ovarian|cervical|vaginal|vulvar|endometriosis|pregnan)', 'Female Reproductive'),
    (r'\b(prostate|testicular|penile|male)', 'Male Reproductive'),
    (r'\b(bladder|urinary|urethra|prostat|incontinen)', 'Urinary'),
    (r'\b(immune|lymph|spleen|thymus|autoimmune)', 'Immune/Lymphatic'),
]

PATHOPHYSIOLOGY_TEMPLATES = {
    'infectious': 'Pathogen invasion -> host immune response -> tissue damage',
    'autoimmune': 'Loss of self-tolerance -> autoantibodies/T-cell attack on self-antigens -> inflammation',
    'genetic': 'Gene mutation -> defective protein -> cellular dysfunction -> clinical phenotype',
    'neoplastic': 'Oncogene activation/tumor suppressor loss -> uncontrolled proliferation -> invasion/metastasis',
    'metabolic': 'Enzyme/hormone deficiency or resistance -> metabolic pathway disruption -> organ dysfunction',
    'degenerative': 'Progressive loss of structure/function -> protein aggregation/oxidative stress -> cell death',
    'vascular': 'Vessel occlusion/rupture -> ischemia/reperfusion -> tissue infarction',
    'traumatic': 'Mechanical force -> tissue disruption -> inflammatory response',
    'toxic': 'Toxin exposure -> cellular injury -> organ dysfunction',
    'default': 'Dysregulation of normal homeostatic mechanisms -> tissue/organ dysfunction',
}

DURATION_RULES = [
    (r'\b(acute|sudden|emergent)', 'Acute (hours to days)'),
    (r'\b(chronic|persistent|long-term|longstanding)', 'Chronic (months to years)'),
    (r'\b(subacute)', 'Subacute (weeks to months)'),
    (r'\b(episodic|recurrent|intermittent)', 'Episodic/Recurrent'),
    (r'\b(lifelong|congenital|genetic)', 'Lifelong'),
    (r'\b(progressive)', 'Progressive (years)'),
]

ONSET_RULES = [
    (r'\b(sudden|abrupt|emergent|stroke|mi|infarction|trauma|injury|anaphylaxis)', 'Sudden'),
    (r'\b(insidious|gradual|slow|progressive|insidious)', 'Insidious/Gradual'),
    (r'\b(congenital|birth|neonatal|infancy)', 'Congenital/Neonatal'),
    (r'\b(childhood|pediatric|adolescent)', 'Childhood/Adolescent'),
    (r'\b(adult|middle.age|elderly)', 'Adulthood'),
]

TRANSMISSION_RULES = [
    (r'\b(infectious|bacteri|viral|fungal|parasit|tb|tuberculosis|hiv|hepatitis|flu|pneumonia|meningitis|sepsis|abscess|cellulitis)', 'Person-to-person / vector-borne / environmental'),
    (r'\b(genetic|hereditary|congenital|chromosome)', 'Non-communicable (genetic)'),
    (r'\b(autoimmune|cancer|degenerative|metabolic|endocrine)', 'Non-communicable'),
    (r'\b(trauma|injury|fracture|burn|poisoning|toxic)', 'Non-communicable'),
    (r'\b(psychiatric|mental|depression|anxiety|schizophrenia)', 'Non-communicable'),
]

COURSE_RULES = [
    (r'\b(acute|self.limited|resolv)', 'Acute, self-limited'),
    (r'\b(chronic|progressive|relapsing|remitting)', 'Chronic, progressive/relapsing-remitting'),
    (r'\b(episodic|intermittent|recurrent)', 'Episodic/Recurrent'),
    (r'\b(lifelong|stable|static)', 'Lifelong, stable'),
    (r'\b(terminal|fatal|prognosis poor)', 'Progressive to terminal'),
    (r'\b(curable|resectable|treatable)', 'Potentially curable with treatment'),
]

SEVERITY_RULES = [
    (r'\b(mild|asymptomatic|incidental)', 'Mild'),
    (r'\b(moderate)', 'Moderate'),
    (r'\b(severe|critical|life.threatening|emergent|fatal)', 'Severe/Life-threatening'),
    (r'\b(mild.to.moderate)', 'Mild to Moderate'),
    (r'\b(moderate.to.severe)', 'Moderate to Severe'),
]

EXTENT_RULES = [
    (r'\b(localized|focal|local|single)', 'Localized'),
    (r'\b(diffuse|generalized|widespread|systemic|multifocal|multisystem)', 'Diffuse/Generalized'),
    (r'\b(metastatic|disseminated)', 'Metastatic/Disseminated'),
    (r'\b(regional|segmental)', 'Regional'),
]

AGE_RULES = [
    (r'\b(neonatal|newborn|infant|baby)', 'Neonates/Infants'),
    (r'\b(child|pediatric|adolescent|teen)', 'Children/Adolescents'),
    (r'\b(young.adult|young)', 'Young Adults'),
    (r'\b(adult|middle.age)', 'Adults'),
    (r'\b(elderly|geriatric|aged|senior|older)', 'Elderly'),
    (r'\b(all.age|any.age|lifespan)', 'All Ages'),
    (r'\b(perinatal|pregnancy|maternal)', 'Pregnancy/Perinatal'),
]

EPIDEMIOLOGY_TEMPLATES = {
    'common': 'Common; high prevalence in general population',
    'rare': 'Rare; low prevalence (<1/2000)',
    'age_related': 'Incidence increases with age',
    'genetic': 'Genetic; family clustering',
    'infectious': 'Endemic/epidemic potential; varies by region',
    'cancer': 'Incidence increases with age; varies by type',
    'autoimmune': 'Female predominance; peak 20-50 years',
    'genetic_rare': 'Rare genetic disorder; birth prevalence ~1/10,000-1/100,000',
}

ICD11_MAP = {
    # Infectious
    'tuberculosis': '1B12.0', 'hiv': '1C62', 'hepatitis b': '1E50', 'hepatitis c': '1E51',
    'malaria': '1F40', 'dengue': '1D60', 'covid': '1D6Y',
    # Neoplastic
    'lung cancer': '2C25.0', 'breast cancer': '2C60.0', 'colorectal': '2B90.0',
    'prostate': '2C61.0', 'leukemia': '2A40.0', 'lymphoma': '2A70.0',
    # Cardiovascular
    'mi': 'BA41.0', 'heart failure': 'BD10.0', 'afib': 'BC81.3', 'hypertension': 'BA00.0',
    # Neurological
    'stroke': '8B20.0', 'alzheimer': '8A20', 'parkinson': '8A00.0', 'ms': '8A10.0',
    'epilepsy': '8A60.0',
    # Respiratory
    'asthma': 'CA20.0', 'copd': 'CA22.0', 'pneumonia': 'CA40.0',
    # GI
    'gerd': 'DA20.0', 'ibs': 'DD10.0', 'ibd': 'DD70.0', 'celiac': 'DD30.0',
    # Endocrine
    'diabetes type 1': '5A10', 'diabetes type 2': '5A11', 'hypothyroid': '5A00.0',
    'hyperthyroid': '5A01.0', 'cushing': '5A20.0',
    # Musculoskeletal
    'ra': 'FA20.0', 'oa': 'FA10.0', 'gout': 'FA25.0',
    # Skin
    'psoriasis': 'EA80.0', 'eczema': 'EA84.0', 'melanoma': '2F20.0',
    # Mental
    'depression': '6A70.0', 'anxiety': '6B00.0', 'bipolar': '6A60.0', 'schizophrenia': '6A20.0',
    # Genetic
    'down': 'LD40.0', 'turner': 'LD41.0', 'klinefelter': 'LD42.0',
    'cf': 'CA23.0', 'sickle': '3A00.0',
    # Default
    'default': 'XX00.0'
}

def classify_disease(title, content):
    """Classify a disease based on title and content."""
    title_lower = title.lower()
    content_lower = content.lower()[:5000]  # First 5000 chars for speed
    
    # Check specific overrides first
    for key, cls in SPECIFIC_CLASSIFICATIONS.items():
        if key in title_lower:
            return cls
    
    # Helper to apply rules
    def apply_rules(text, rules, default):
        for pattern, value in rules:
            if re.search(pattern, text, re.IGNORECASE):
                return value
        return default
    
    # Cause
    cause = apply_rules(title_lower + ' ' + content_lower, CAUSE_RULES, 'Multifactorial/Unknown')
    
    # Organ
    organ = apply_rules(title_lower + ' ' + content_lower, ORGAN_RULES, 'Multiple/General')
    
    # Pathophysiology
    patho = 'Unknown'
    for key, template in PATHOPHYSIOLOGY_TEMPLATES.items():
        if key in cause.lower() or key in title_lower:
            patho = template
            break
    if patho == 'Unknown':
        patho = PATHOPHYSIOLOGY_TEMPLATES['default']
    
    # Duration
    duration = apply_rules(title_lower + ' ' + content_lower, DURATION_RULES, 'Variable')
    
    # Onset
    onset = apply_rules(title_lower + ' ' + content_lower, ONSET_RULES, 'Variable')
    
    # Transmission
    transmission = apply_rules(title_lower + ' ' + content_lower, TRANSMISSION_RULES, 'Non-communicable')
    
    # Course
    course = apply_rules(title_lower + ' ' + content_lower, COURSE_RULES, 'Variable')
    
    # Severity
    severity = apply_rules(title_lower + ' ' + content_lower, SEVERITY_RULES, 'Variable')
    
    # Extent
    extent = apply_rules(title_lower + ' ' + content_lower, EXTENT_RULES, 'Variable')
    
    # Age Group
    age_group = apply_rules(title_lower + ' ' + content_lower, AGE_RULES, 'Adults')
    
    # Epidemiology
    epi = EPIDEMIOLOGY_TEMPLATES['common']
    for key, template in EPIDEMIOLOGY_TEMPLATES.items():
        if key in cause.lower() or key in title_lower:
            epi = template
            break
    
    # ICD-11
    icd = ICD11_MAP['default']
    for key, code in ICD11_MAP.items():
        if key in title_lower:
            icd = code
            break
    
    return {
        'cause': cause,
        'organ': organ,
        'pathophysiology': patho,
        'duration': duration,
        'onset': onset,
        'transmission': transmission,
        'course': course,
        'severity': severity,
        'extent': extent,
        'age_group': age_group,
        'epidemiology': epi,
        'icd11': icd
    }

def generate_classification_section(cls):
    """Generate LaTeX Classification section."""
    items = [
        ('Cause', cls['cause']),
        ('Organ System', cls['organ']),
        ('Pathophysiology', cls['pathophysiology']),
        ('Duration', cls['duration']),
        ('Onset', cls['onset']),
        ('Mode of Transmission', cls['transmission']),
        ('Clinical Course', cls['course']),
        ('Severity', cls['severity']),
        ('Extent of Disease', cls['extent']),
        ('Age Group', cls['age_group']),
        ('Epidemiology', cls['epidemiology']),
        ('ICD-11 Code', cls['icd11']),
    ]
    
    lines = ['\\section{Classification}', '']
    lines.append('\\begin{description}[font=\\normalfont\\bfseries,leftmargin=3em,labelwidth=2.5em]')
    for label, value in items:
        lines.append(f'  \\item[{label}] {value}')
    lines.append('\\end{description}')
    lines.append('')
    return '\n'.join(lines)

def process_file(filepath):
    """Process a single disease file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract title
    m = re.search(r'\\chapter\{([^}]+)\}', content)
    if not m:
        return False, 'No chapter found'
    title = m.group(1)
    
    # Check if Classification already exists
    if '\\section{Classification}' in content:
        return False, 'Already has Classification'
    
    # Classify
    cls = classify_disease(title, content)
    
    # Generate section
    class_section = generate_classification_section(cls)
    
    # Insert after \section{Overview}
    pattern = r'(\\section\{Overview\})'
    match = re.search(pattern, content)
    if not match:
        return False, 'No Overview section found'
    
    # Find the end of Overview section (next \section or end of file)
    # Simpler: insert right after \section{Overview} and its content, before next \section
    # We'll insert before the next \section after Overview
    overview_pos = match.end()
    
    # Find next \section after Overview
    next_section = re.search(r'\\section\{', content[overview_pos:])
    if next_section:
        insert_pos = overview_pos + next_section.start()
        new_content = content[:insert_pos] + class_section + '\n' + content[insert_pos:]
    else:
        # No next section, append before end
        new_content = content[:overview_pos] + class_section + '\n' + content[overview_pos:]
    
    # Write
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True, f'Added Classification to {filepath.name}'

def main():
    results = {'added': 0, 'skipped': 0, 'errors': 0}
    for filepath in files:
        try:
            success, msg = process_file(filepath)
            if success:
                results['added'] += 1
                print(f'✓ {filepath.name}')
            else:
                results['skipped'] += 1
                if 'error' in msg.lower():
                    results['errors'] += 1
                    print(f'✗ {filepath.name}: {msg}')
        except Exception as e:
            results['errors'] += 1
            print(f'✗ {filepath.name}: {e}')
    
    print(f"\nSummary: {results['added']} added, {results['skipped']} skipped, {results['errors']} errors")

if __name__ == '__main__':
    main()