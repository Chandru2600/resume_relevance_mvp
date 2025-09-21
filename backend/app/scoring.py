# backend/app/scoring.py
from fuzzywuzzy import fuzz
import json

def fuzzy_skill_fraction(required_skills, resume_text, threshold=70):
    """
    For each required skill, see if resume_text contains a fuzzy match above threshold.
    Return fraction matched and list of missing skills.
    """
    matched = 0
    missing = []
    resume = resume_text.lower()
    for rs in required_skills:
        rs_clean = rs.lower()
        # quick substring check
        if rs_clean in resume:
            matched += 1
            continue
        # else try fuzzy on small tokens
        # test by sliding window of resume words (naive)
        best = 0
        for chunk in [rs_clean]:
            score = fuzz.partial_ratio(chunk, resume)
            if score > best:
                best = score
        if best >= threshold:
            matched += 1
        else:
            missing.append(rs)
    frac = matched / (len(required_skills) if required_skills else 1)
    return frac, missing

def compute_final_score(h_skill_frac):
    # MVP: simple mapping: weighted only on hard skills for speed
    score = round(100 * (0.8 * h_skill_frac + 0.2 * 0.0), 2)  # reserved space for semantic later
    return score

def verdict_from_score(score):
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"
