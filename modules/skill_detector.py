# modules/skill_detector.py
import json
import spacy
import re

# -----------------------------
# Load Spacy English model
# -----------------------------
# If the model isn't installed, try to install it automatically.
# This makes the app easier to run for users who haven't downloaded the model.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Note: this requires internet access the first time.
    from spacy.cli import download as spacy_download

    spacy_download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# -----------------------------
# Load skills and synonyms from JSON
# -----------------------------
with open("data/skills.json") as f:
    data = json.load(f)
    SKILLS = set(data["skills"])          # Official skills
    SYNONYMS = data.get("synonyms", {})   # Synonyms mapping

# -----------------------------
# Skill Detection Function
# -----------------------------
def detect_skills(cv_text):
    """
    Detect skills from CV text using:
    - NLP tokenization & noun chunks
    - Predefined skill list
    - Synonyms mapping
    """
    detected = set()
    text_lower = cv_text.lower()
    
    # 1️⃣ Check synonyms first
    for short, full in SYNONYMS.items():
        pattern = r'\b' + re.escape(short.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected.add(full)
    
    # 2️⃣ Check predefined skills (single & multi-word)
    for skill in SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected.add(skill)
    
    # 3️⃣ NLP: detect multi-word noun phrases
    doc = nlp(cv_text)
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        if phrase in SKILLS:
            detected.add(phrase)
    
    return list(detected)