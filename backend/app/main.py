from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# In-memory storage of JDs
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
    Extract skills from JD text under 'Skills' or 'Skills Required'
    """
    skills = []
    capture = False
    for line in jd_text.splitlines():
        line = line.strip()
        if line.lower().startswith("skills"):
            capture = True
            continue
        if capture:
            if line.startswith("-"):
                skills.append(line[1:].strip())
            elif line == "":
                break  # stop at empty line
    return skills

def extract_skills_from_resume(resume_text: str, jd_skills: List[str]) -> List[str]:
    """
    Compare resume text with JD skills to find matched skills
    """
    matched = []
    resume_lower = resume_text.lower()
    for skill in jd_skills:
        if skill.lower() in resume_lower:
            matched.append(skill)
    return matched

def compute_relevance(jd_text: str, resume_text: str):
    jd_skills = extract_skills_from_jd(jd_text)
    matched_skills = extract_skills_from_resume(resume_text, jd_skills)
    missing_skills = list(set(jd_skills) - set(matched_skills))
    score = int(len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
    verdict = "Good fit" if score >= 60 else "Poor fit"
    return {
        "score": score,
        "verdict": verdict,
        "missing_skills": missing_skills,
        "matched_skills": matched_skills
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
