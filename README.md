# Resume Relevance MVP

Automated Resume Evaluation Tool that scores resumes against Job Descriptions (JD) by analyzing skills. Outputs Relevance Score, Verdict, and Missing Skills/Elements.

## Project Structure

- **backend/** — FastAPI backend  
- **frontend/** — Streamlit frontend  

## Features

- Extracts only the Skills section from the JD
- Evaluates resumes in PDF or DOCX format
- Outputs Relevance Score, Verdict, and Missing Skills/Elements

## Installation

### Clone the repository

##Setup Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

##Setup Frontend
cd ../frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py

##Usage
1.Enter or paste the Job Description (JD)
2.Upload the resume (PDF/DOCX)
3.Click Evaluate Resume
4.View Relevance Score, Verdict, and Missing Skills/Elements
