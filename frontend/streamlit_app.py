import streamlit as st
import requests
from io import BytesIO
import pdfplumber
import docx

BACKEND_URL = "https://resume-relevance-mvp.onrender.com"

# ----------------------------
# Custom CSS
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #f75252 1%, #f7cc74 100%);}
[data-testid="stHeader"] {background-color: transparent;}
.blue-gradient {background: linear-gradient(90deg, #4fc3f7 0%, #b2ebf2 100%);
    color: #1a237e !important; font-weight: bold; padding: 10px 18px;
    border-radius: 10px; margin-bottom: 12px; font-size: 18px;}
.green-gradient {background: linear-gradient(90deg, #A6F1A6 0%, #80CBC4 100%);
    color: #005B3E !important; font-weight: bold; padding: 10px 18px;
    border-radius: 10px; margin-bottom: 12px; font-size: 18px;}
.score-box {background: linear-gradient(90deg, #80deea 0%, #a5d6a7 100%);
    color: #004d40; padding: 10px; border-radius: 10px; font-weight: bold;
    font-size: 22px; text-align: center; box-shadow: 0 3px 8px rgba(0,0,0,0.07);
    margin-bottom: 12px;}
.verdict-box.good {background: #d2ffd2; color: #388e3c; border-left: 6px solid #81c784;
    padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 18px;
    margin-bottom: 10px;}
.verdict-box.bad {background: #ffeaea; color: #d32f2f; border-left: 6px solid #e57373;
    padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 18px;
    margin-bottom: 10px;}
.verdict-box.verygood {background: #d0f0fd; color: #0277bd; border-left: 6px solid #4fc3f7;
    padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 18px;
    margin-bottom: 10px;}
.verdict-box.excellent {background: #e0ffe0; color: #2e7d32; border-left: 6px solid #81c784;
    padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 18px;
    margin-bottom: 10px;}
.missing-skill {background: #fff3e0; color: #e65100; border-left: 5px solid #FFD54F;
    padding: 8px 16px; border-radius: 7px; font-weight: bold; margin-bottom: 7px;}
.matched-skill {background: #e0f7fa; color: #00695c; border-left: 5px solid #4db6ac;
    padding: 8px 16px; border-radius: 7px; font-weight: bold; margin-bottom: 7px;}
</style>
""", unsafe_allow_html=True)

st.title("Automated Resume Relevance")

# ----------------------------
# JD Section
st.header("Step 1: Enter Job Description (JD)")
st.markdown('<div class="blue-gradient">Please provide the job details and requirements.</div>', unsafe_allow_html=True)
title = st.text_input("Job Title")
jd_text = st.text_area("Paste Job Description here")

# ----------------------------
# Resume Section
st.header("Step 2: Upload Resume")
st.markdown('<div class="green-gradient">Upload your PDF or DOCX resume file.</div>', unsafe_allow_html=True)
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# ----------------------------
# Extract resume text
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
    return ""

# ----------------------------
# Evaluate Resume
if st.button("Evaluate Resume"):
    if not title:
        st.error("🚩 Please enter Job Title.")
    elif not jd_text.strip():
        st.error("🚩 Please paste Job Description text.")
    elif resume_file is None:
        st.error("🚩 Please upload your resume file.")
    else:
        with st.spinner("🔄 Sending JD..."):
            jd_resp = requests.post(f"{BACKEND_URL}/jd", json={"title": title, "jd": jd_text})
        if jd_resp.status_code != 200:
            st.error(f"Error sending JD: {jd_resp.text}")
        else:
            jd_id = jd_resp.json().get("jd_id")
            st.success(f"JD processed successfully! JD ID: {jd_id}")

            with st.spinner("🔎 Extracting resume text..."):
                resume_text = extract_resume_text(resume_file)

            with st.spinner("📊 Evaluating resume..."):
                resume_resp = requests.post(f"{BACKEND_URL}/evaluate_resume",
                                            json={"jd_id": jd_id, "resume_text": resume_text})
            if resume_resp.status_code != 200:
                st.error(f"Error evaluating resume: {resume_resp.text}")
            else:
                result = resume_resp.json()
                st.success("✅ Resume evaluated successfully!")

                # Score
                score = result.get("score", 0)
                st.subheader("Relevance Score")
                st.markdown(f"<div class='score-box'>{score} / 100</div>", unsafe_allow_html=True)

                # Verdict
                verdict = result.get("verdict", "N/A").lower()
                verdict_class = "bad"
                if verdict == "excellent":
                    verdict_class = "excellent"
                elif verdict == "very good":
                    verdict_class = "verygood"
                elif verdict == "good":
                    verdict_class = "good"

                st.subheader("Verdict")
                st.markdown(f"<div class='verdict-box {verdict_class}'>{verdict.title()}</div>", unsafe_allow_html=True)

                # Matched Skills
                matched_skills = result.get("matched_skills", [])
                if matched_skills:
                    st.subheader("Matched Skills")
                    for skill in matched_skills:
                        st.markdown(f"<div class='matched-skill'>{skill}</div>", unsafe_allow_html=True)

                # Missing Skills
                missing_skills = result.get("missing_skills", [])
                st.subheader("Missing Skills/Elements")
                if missing_skills:
                    for skill in missing_skills:
                        st.markdown(f"<div class='missing-skill'>{skill}</div>", unsafe_allow_html=True)
                else:
                    st.success("🎉 All required skills are present!")
