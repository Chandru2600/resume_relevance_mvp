from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uuid
import re

app = FastAPI()

# In-memory JD storage
JDS = {}

# ----------------------------
# Models
# ----------------------------
class JDInput(BaseModel):
    title: str
    jd: str

class ResumeInput(BaseModel):
    jd_id: str
    resume_text: str

# ----------------------------
# Helper functions
# ----------------------------
def extract_skills_from_jd(jd_text: str) -> List[str]:
    """
    Extract skills from JD text regardless of formatting.
    Handles:
    - Bullets (-, *, •)
    - Colon-separated sections (Programming: Python, C)
    - Inline sentences (Skills required: Python, Django)
    """
    skills = []

    for line in jd_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Remove bullets
        line = re.sub(r"^[-*•]\s*", "", line)

        # Extract after colon if exists
        if ':' in line:
            parts = line.split(":", 1)
            line = parts[1].strip()

        # Split by comma or 'and'
        line_skills = [s.strip().lower() for s in re.split(r",|\band\b", line) if s.strip()]
        skills.extend(line_skills)

    # Remove duplicates
    return list(set(skills))

def extract_skills_from_resume(resume_text: str, jd_skills: List[str]) -> List[str]:
    """
    Match only JD-extracted skills in resume text
    """
    resume_text_clean = re.sub(r"[^\w\s]", "", resume_text.lower())
    matched = [skill for skill in jd_skills if skill in resume_text_clean]
    return matched

def compute_relevance(jd_text: str, resume_text: str):
    jd_skills = extract_skills_from_jd(jd_text)
    matched_skills = extract_skills_from_resume(resume_text, jd_skills)
    missing_skills = list(set(jd_skills) - set(matched_skills))
    score = int(len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0

    # 4-level verdict
    if score >= 90:
        verdict = "Excellent"
    elif score >= 80:
        verdict = "Very Good"
    elif score >= 70:
        verdict = "Good"
    else:
        verdict = "Bad"

    return {
        "score": score,
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }

# ----------------------------
# Endpoints
# ----------------------------
@app.post("/jd")
def upload_jd(jd_input: JDInput):
    jd_id = str(uuid.uuid4())
    JDS[jd_id] = jd_input.jd
    return {"jd_id": jd_id}

@app.post("/evaluate_resume")
def evaluate_resume(resume_input: ResumeInput):
    jd_text = JDS.get(resume_input.jd_id)
    if not jd_text:
        return {"error": "JD not found"}
    result = compute_relevance(jd_text, resume_input.resume_text)
    return result
