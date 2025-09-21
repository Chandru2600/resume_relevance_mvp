import streamlit as st
import requests
from io import BytesIO
import pdfplumber
import docx

BACKEND_URL = "http://127.0.0.1:8000"

# ----------------------------
# Light background
# ----------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #545252;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 20px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Automated Resume Relevance")

# ----------------------------
# JD Section
# ----------------------------
st.header("Step 1: Enter Job Description (JD)")
title = st.text_input("Job Title")
jd_text = st.text_area("Paste Job Description here (use 'Skills' section)")

# ----------------------------
# Resume Section
# ----------------------------
st.header("Step 2: Upload Resume")
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# ----------------------------
# Helper: Extract resume text
# ----------------------------
def extract_resume_text(file):
    if file.name.endswith(".pdf"):
        file_bytes = BytesIO(file.getvalue())
        text = ""
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(BytesIO(file.getvalue()))
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return ""

# ----------------------------
# Evaluate Button
# ----------------------------
if st.button("Evaluate Resume"):
    if not title:
        st.error("Enter Job Title")
    elif not jd_text.strip():
        st.error("Enter Job Description text")
    elif resume_file is None:
        st.error("Upload Resume file")
    else:
        # 1️⃣ Send JD to backend
        with st.spinner("Sending JD text..."):
            jd_resp = requests.post(
                f"{BACKEND_URL}/jd",
                json={"title": title, "jd": jd_text}
            )
        if jd_resp.status_code != 200:
            st.error(f"Error sending JD: {jd_resp.text}")
        else:
            jd_id = jd_resp.json().get("jd_id")
            st.success(f"JD processed successfully! JD ID: {jd_id}")

            # 2️⃣ Extract resume text locally
            with st.spinner("Extracting resume text..."):
                resume_text = extract_resume_text(resume_file)

            # 3️⃣ Send resume for evaluation
            with st.spinner("Evaluating resume..."):
                resume_resp = requests.post(
                    f"{BACKEND_URL}/evaluate_resume",
                    json={"jd_id": jd_id, "resume_text": resume_text}
                )

            if resume_resp.status_code != 200:
                st.error(f"Error evaluating resume: {resume_resp.text}")
            else:
                result = resume_resp.json()
                st.success("Resume evaluated successfully!")

                # ----------------------------
                # Display Relevance Score
                # ----------------------------
                score = result.get("score", 0)
                st.subheader("Relevance Score")
                st.markdown(
                    f"<div style='color:#ffffff; background-color:#4CAF50; padding:10px; border-radius:6px; font-weight:bold; font-size:18px'>{score} / 100</div>",
                    unsafe_allow_html=True
                )

                # ----------------------------
                # Display Verdict
                # ----------------------------
                verdict = result.get("verdict", "N/A")
                verdict_color = "#00529B" if verdict == "Good fit" else "#D8000C"
                st.subheader("Verdict")
                st.markdown(
                    f"<div style='color:{verdict_color}; background-color:#BDE5F8; padding:10px; border-radius:6px; font-weight:bold; font-size:18px'>{verdict}</div>",
                    unsafe_allow_html=True
                )

                # ----------------------------
                # Display Missing Skills
                # ----------------------------
                missing_skills = result.get("missing_skills", [])
                st.subheader("Missing Skills/Elements")
                if missing_skills:
                    for skill in missing_skills:
                        st.markdown(
                            f"<div style='color:#D8000C; background-color:#FFDDDD; padding:8px; margin:4px 0; border-radius:6px; font-weight:bold'>{skill}</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.success("All required skills are present! 🎉")
