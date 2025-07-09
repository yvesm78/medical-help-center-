import streamlit as st
import pandas as pd
import docx
import google.generativeai as genai

# === CONFIGURE GEMINI ===
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# === PAGE CONFIG ===
st.set_page_config(page_title="🩺 AI Medical Assistant", layout="wide", page_icon="🧠")

# === STYLING ===
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
    .result-box {
        background-color: #e9fcef;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #2ECC71;
        font-size: 1.05em;
    }
    .chat-box {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("<div class='main-header'>🧠 AI Medical Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload patient reports, receive AI medical recommendations, and ask follow-up questions below.</div>", unsafe_allow_html=True)

# === SESSION STATE ===
if "analysis_context" not in st.session_state:
    st.session_state.analysis_context = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === FILE UPLOAD ===
uploaded_file = st.file_uploader("📤 Upload patient file", type=["csv", "xlsx", "docx"])

# === GET ANALYSIS BUTTON ===
if uploaded_file and st.button("🧾 Get Analysis and Recommendations"):
    with st.spinner("Analyzing patient file..."):
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
        A doctor has uploaded a patient medical report. Please analyze and summarize the following:
        1. Possible diagnosis or health condition
        2. Recommended medications or treatments
        3. Lifestyle and practical health advice
        4. Referral suggestions (if needed)

        Patient Report:
        ----------------------
        {file_text}
        """

        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            st.session_state.analysis_context = f"Patient Report:\n{file_text}\n\nInitial Analysis:\n{output}"
            st.markdown("### 🩺 AI Diagnosis & Recommendations")
            st.markdown(f"<div class='result-box'>{output}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error("❌ Failed to generate AI recommendations.")
            st.exception(e)

# === FOLLOW-UP CHAT SECTION ===
if st.session_state.analysis_context:
    st.markdown("---")
    st.markdown("### 💬 Ask Follow-Up Questions About This Patient or Report")

    # Show chat history
    for chat in st.session_state.chat_history:
        sender = "👨‍⚕️ You" if chat["role"] == "user" else "🤖 AI"
        st.markdown(f"<div class='chat-box'><strong>{sender}:</strong><br>{chat['content']}</div>", unsafe_allow_html=True)

    # Chat input
    user_question = st.chat_input("Ask a follow-up question...")

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        followup_prompt = (
            f"{st.session_state.analysis_context}\n\n"
            f"Doctor's follow-up question: {user_question}\n\n"
            "Answer as a helpful medical assistant."
        )

        try:
            reply = model.generate_content(followup_prompt).text.strip()
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
        except Exception as e:
            st.error("⚠️ AI failed to answer your question.")
            st.exception(e)

# === FOOTER ===
st.markdown("---")
st.markdown("Made with ❤️ for doctors | Powered by Google Gemini")
