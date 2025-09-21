# Resume Relevance MVP (FastAPI + Streamlit)

## Prereqs
- Python 3.9+ (recommended 3.10)
- pip

## Setup & run backend
1. Open terminal:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
