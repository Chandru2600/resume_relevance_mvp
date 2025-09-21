# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class JDCreate(BaseModel):
    title: str
    raw_text: str
    skills: List[str]

class ResumeCreate(BaseModel):
    filename: str
    raw_text: str

class EvaluationOut(BaseModel):
    resume_id: int
    jd_id: int
    score: float
    verdict: str
    missing_skills: List[str]
