# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.types import JSON
from datetime import datetime
from .db import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    raw_text = Column(Text)
    skills_json = Column(Text)  # simple JSON stringified array
    created_at = Column(DateTime, default=datetime.utcnow)

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    raw_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer)
    jd_id = Column(Integer)
    score = Column(Float)
    verdict = Column(String)
    missing_skills = Column(Text)  # JSON-like text
    created_at = Column(DateTime, default=datetime.utcnow)
