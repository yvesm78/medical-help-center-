
import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURE GOOGLE GEMINI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# --- LOAD CSV DATA ---
try:
    df = pd.read_csv('chatbot_qa.csv')
    qa_pairs = [f"Q: {q}\nA: {a}" for q, a in zip(df['Question'], df['Answer'])]
    context = "\n".join(qa_pairs)
except FileNotFoundError:
    st.error("Data file 'chatbot_qa.csv' not found.")
    st.stop()

# === PAGE CONFIG ===
st.set_page_config(page_title="Kepler CampusBot", layout="wide")

# === CUSTOM STYLING ===
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .stApp {
        background-color: #f5f7fa;
    }
    .kepler-header {
        color: #2A527A;
        text-align: center;
        margin-top: -20px;
    }
    .chat-box {
        border: 2px solid #0C2340;
        border-radius: 12px;
        padding: 1rem;
        background-color: white;
        margin-bottom: 1rem;
    }
    .user-box {
        border-left: 6px solid #0C2340;
        background-color: #e8f1fb;
    }
    .bot-box {
        border-left: 6px solid #2ECC71;
        background-color: #e9fcef;
    }
    </style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.image("kepler-logo.png", width=120)
    st.header("Navigation")
    if st.button("💬 Chatbot", use_container_width=True):
        st.query_params['page'] = 'chat'
        st.rerun()
    if st.button("ℹ About Me", use_container_width=True):
        st.query_params['page'] = 'about'
        st.rerun()

# === MAIN PAGE ROUTING ===
current_page = st.query_params.get('page', 'chat')

if current_page == "chat":
    st.image("kepler-logo.png", width=120)
    st.markdown("<h2 class='kepler-header'>Welcome to Kepler CampusBot 🎓</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Ask about Kepler College rules, policies, or services.</p>", unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-box user-box'><strong>🧑 You:</strong><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-box bot-box'><strong>🤖 CampusBot:</strong><br>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your question here...")
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        prompt = f"You are Kepler CampusBot. Use this Q&A to help answer:\n{context}\n\nUser: {user_input}"
        response = model.generate_content(prompt)
        answer = response.text.strip()
        st.session_state.history.append({"role": "assistant", "content": answer})
        st.rerun()

elif current_page == "about":
    st.title("About Kepler College Chatbot")
    st.markdown("""
    I am CampusBot, an AI assistant designed to help you with a wide range of tasks and questions about Kepler College. 
    My knowledge is based on official college resources, and my goal is to provide you with instant, accurate information.
    """)
    st.markdown("---")
    st.markdown("""
    ### Contact Us
    - *Phone:* +250789773042
    - *Website:* [keplercollege.ac.rw](https://keplercollege.ac.rw)
    - *Admissions:* [admissions@keplercollege.ac.rw](mailto:admissions@keplercollege.ac.rw)
    """)
