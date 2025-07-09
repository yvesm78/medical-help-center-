import streamlit as st
import pandas as pd
import docx
import google.generativeai as genai

# === GEMINI CONFIG ===
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# === PAGE CONFIG ===
st.set_page_config(page_title="🩺 AI Medical Agent", layout="wide", page_icon="🧠")

# === HEADER ===
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        font-size: 2.5em;
        color: #2A527A;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        font-size: 1.1em;
        color: #555;
        margin-bottom: 2rem;
    }
    .stApp {
        background-color: #f5f7fa;
    }
    .file-uploader {
        border: 2px dashed #2A527A;
        padding: 1rem;
        border-radius: 10px;
        background-color: #ffffff;
    }
    .result-box {
        background-color: #e9fcef;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #2ECC71;
        font-size: 1.05em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🧠 AI Medical Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload patient reports (.csv, .xlsx, .docx) to receive AI-powered medical analysis and recommendations.</div>", unsafe_allow_html=True)

# === FILE UPLOAD ===
uploaded_file = st.file_uploader("📤 Upload patient file", type=["csv", "xlsx", "docx"])

# === ANALYSIS BUTTON ===
if uploaded_file and st.button("🧾 Get Analysis and Recommendations"):
    with st.spinner("Analyzing file... please wait"):
        file_text = ""

        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            file_text = df.to_string(index=False)

        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
            file_text = df.to_string(index=False)

        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            file_text = "\n".join([p.text for p in doc.paragraphs])

        # === PROMPT TO GEMINI ===
        prompt = f"""
        A doctor has uploaded a patient medical or lab report. Analyze it and respond with:
        1. Health diagnosis or concerns
        2. Suggested medications or treatments
        3. Lifestyle or health advice
        4. Referral recommendations (if needed)

        Patient report:
        ----------------------
        {file_text}
        """

        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            st.markdown("### 🩺 AI Diagnosis & Recommendations")
            st.markdown(f"<div class='result-box'>{output}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("❌ Gemini failed to generate a response.")
            st.exception(e)

# === FOOTER ===
st.markdown("---")
st.markdown("Made with ❤️ for doctors | Powered by Google Gemini")
