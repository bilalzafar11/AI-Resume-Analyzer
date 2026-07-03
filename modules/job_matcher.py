# modules/job_matcher.py

from rapidfuzz import fuzz

# Optional: synonyms mapping (same as skill_detector)
SYNONYMS = {
    "ML": "Machine Learning",
    "DL": "Deep Learning",
    "JS": "JavaScript",
    "NLP": "Natural Language Processing",
    "AI": "Machine Learning",
    "GEN AI": "Machine Learning",
    "GENERATIVE AI": "Machine Learning",
    "ARTIFICIAL INTELLIGENCE": "Machine Learning"
}

def normalize_skill(skill):
    """Map synonyms to standard skill name"""
    return SYNONYMS.get(skill, skill)

def match_score(cv_skills, job_skills, core_skills=None):
    """
    Calculate professional match score between CV skills and Job description skills.

    Args:
        cv_skills (list): Skills detected from CV
        job_skills (list): Skills from Job description
        core_skills (list, optional): Skills considered very important

    Returns:
        score (int): Match percentage
        matched_skills (list)
        missing_skills (list)
        breakdown (dict): skill: matched(True/False)
    """
    core_skills = core_skills or []
    
    # Normalize synonyms
    cv_skills = [normalize_skill(s) for s in cv_skills]
    job_skills = [normalize_skill(s) for s in job_skills]

    cv_set = set([s.lower() for s in cv_skills])
    
    # Improve job_skills parsing: handle both comma-separated and space-separated skills
    processed_job_skills = []
    
    for skill in job_skills:
        # Split by comma first
        comma_split = [s.strip() for s in skill.split(",")]
        
        for sub_skill in comma_split:
            if not sub_skill:
                continue
                
            # If no commas were in original input, try to split space-separated
            if "," not in skill:
                # First, check for known multi-word skills
                words = sub_skill.split()
                if len(words) > 1:
                    # Try to match consecutive words as multi-word skills
                    found_multiword = False
                    for i in range(len(words)):
                        for j in range(i+2, len(words)+1):
                            phrase = " ".join(words[i:j]).lower()
                            # Check if this phrase matches any cv skill
                            if phrase in cv_set:
                                processed_job_skills.append(phrase)
                                found_multiword = True
                    
                    # If no multi-word matches found, add individual words
                    if not found_multiword:
                        processed_job_skills.extend([w for w in words if w])
                else:
                    processed_job_skills.append(sub_skill)
            else:
                processed_job_skills.append(sub_skill)
    
    job_set = set([s.lower() for s in processed_job_skills if s])

    matched_skills = []
    breakdown = {}

    for skill in job_set:
        matched = False
        # Exact match
        if skill in cv_set:
            matched = True
        else:
            # Optional: fuzzy match (similar spelling)
            for cv_skill in cv_set:
                if fuzz.ratio(skill, cv_skill) >= 75:  # 75% similarity threshold
                    matched = True
                    break
        breakdown[skill] = matched
        if matched:
            matched_skills.append(skill)

    # Weighted score: core skills = 2x
    total_weight = len(job_set) + len([s for s in job_set if s in core_skills])
    matched_weight = len(matched_skills) + len([s for s in matched_skills if s in core_skills])
    score = int((matched_weight / total_weight) * 100) if total_weight > 0 else 0

    missing_skills = [s for s in job_set if s not in matched_skills]

    return score, matched_skills, missing_skills, breakdown