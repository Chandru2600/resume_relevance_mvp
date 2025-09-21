# backend/app/utils_parse.py
import fitz  # PyMuPDF
import docx2txt
import re

def extract_text_from_pdf(path: str) -> str:
    text = []
    doc = fitz.open(path)
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)

def extract_text_from_docx(path: str) -> str:
    return docx2txt.process(path)

def extract_text_from_file(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif lower.endswith(".docx") or lower.endswith(".doc"):
        return extract_text_from_docx(path)
    else:
        raise ValueError("Unsupported file type")

def simple_skill_extractor_from_jd(text: str):
    """
    Naive skill extraction: look for lines containing keywords like 'skills', 'requirements', or comma lists.
    This is intentionally simple for the MVP.
    """
    text = text.replace("\r", "\n")
    skills = []
    # Common patterns
    # 1) Lines starting with '- ', '* ', or numbered lists
    for line in text.splitlines():
        l = line.strip()
        if len(l) == 0: 
            continue
        # If line contains commas and contains keywords like 'skill' or 'experience' or is in a skills block
        if re.search(r"skill|requirement|responsibilit|experience", l, re.IGNORECASE) or ("," in l and len(l.split(",")) <= 12):
            parts = re.split(r",|;|-|\\||/| and ", l)
            for p in parts:
                p = p.strip()
                if len(p) >= 2 and len(p) <= 60 and len(p.split()) <= 6:
                    skills.append(p)
    # fallback: take words after 'skills:' or 'must have'
    m = re.search(r"skills?:\s*(.*)", text, re.IGNORECASE)
    if m:
        tail = m.group(1)
        parts = re.split(r",|;|\\||/| and ", tail)
        for p in parts:
            p = p.strip()
            if p:
                skills.append(p)
    # Clean & dedupe
    cleaned = []
    for s in skills:
        s = re.sub(r"[^A-Za-z0-9\+\#\.\- ]", " ", s)
        s = " ".join(s.split())
        if len(s) > 1 and s.lower() not in [c.lower() for c in cleaned]:
            cleaned.append(s)
    return cleaned
