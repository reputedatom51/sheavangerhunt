import streamlit as st
import smtplib
from email.mime.text import MIMEText
import requests
import time
import random

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="The Invasion", page_icon="🏆", layout="centered")

# --- 2. SECURITY CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stTextInput > div > div > input { 
        text-align: center; text-transform: uppercase; 
        font-weight: bold; font-size: 20px; 
        background-color: #262730; color: white; 
    }
    h1 { text-align: center; color: #d32f2f; border-bottom: 2px solid #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE BRAIN (JsonBin Connection) ---
def get_global_stage():
    try:
        # We add a random number to the URL to prevent "Caching" (forcing a fresh read)
        bust_cache = random.randint(1, 10000)
        url = f"https://api.jsonbin.io/v3/b/{st.secrets['jsonbin']['bin_id']}/latest?buster={bust_cache}"
        headers = {"X-Master-Key": st.secrets["jsonbin"]["api_key"]}
        response = requests.get(url, headers=headers)
        return response.json()['record']['stage']
    except:
        return 0 

def update_global_stage(new_stage):
    try:
        url = f"https://api.jsonbin.io/v3/b/{st.secrets['jsonbin']['bin_id']}"
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": st.secrets["jsonbin"]["api_key"]
        }
        requests.put(url, json={"stage": new_stage}, headers=headers)
    except:
        pass

# --- 4. EMAIL NOTIFICATION ---
def send_notification(stage_name):
    if "email" in st.secrets:
        try:
            sender = st.secrets["email"]["username"]
            password = st.secrets["email"]["password"]
            recipients = st.secrets["email"]["recipients"]
            
            msg = MIMEText(f"He cleared {stage_name}. Global stage updated.")
            msg['Subject'] = f"🚨 UPDATE: {stage_name} Cleared!"
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())
        except:
            pass

# --- 5. GAME DATA ---
stages = [
    {"title": "THE CHALLENGE", "key": "intro", "clue": "Type ACCEPT to start."},
    {"title": "MATCH 1: THE TRAINING", "key": "gym", "clue": "Go to the Gym. Find the treadmill."},
    {"title": "MATCH 2: THE MOLE", "key": "resident", "clue": "Find the resident in Room 204."},
    {"title": "MATCH 3: THE TAPE STUDY", "key": "library", "clue": "Find the book 'Leadership 101'."},
    {"title": "MATCH 4: MANAGEMENT", "key": "rd", "clue": "Go find my RD."},
    {"title": "MAIN EVENT: THE GHOST", "key": "jterm", "clue": "It is with a former RA."}
]

# --- 6. APP LOGIC ---

# 1. Sync with Cloud (Background Check)
if "stage" not in st.session_state:
    st.session_state.stage = get_global_stage()

# Only pull from cloud if cloud is AHEAD of us (prevents lagging backward)
global_stage = get_global_stage()
if global_stage > st.session_state.stage:
    st.session_state.stage = global_stage
    st.rerun()

# 2. Display UI
progress = st.session_state.stage / len(stages)
st.progress(progress)
st.title("THE INVASION")

if st.session_state.stage >= len(stages):
    st.balloons()
    st.success("🏆 CHAMPION! 🏆")
    st.write(f"Go claim your prize at **{st.secrets['locations']['final']}**.")
    
    if st.button("Reset Game (Global)"):
        update_global_stage(0)
        st.session_state.stage = 0
        st.rerun()
else:
    current = stages[st.session_state.stage]
    st.subheader(current["title"])
    st.markdown(current["clue"])
    
    if st.button("🔄 Sync Progress"):
        st.rerun()
    
    with st.form(key="game_form"):
        user_input = st.text_input("ENTER PASSWORD")
        submit = st.form_submit_button("SUBMIT")
        
        if submit:
            correct_password = st.secrets["passwords"][current["key"]]
            
            if user_input.strip().upper() == correct_password:
                # --- THE FIX IS HERE ---
                
                # 1. Update LOCAL state immediately (Instant visual change)
                st.session_state.stage += 1
                
                # 2. Update GLOBAL state (Cloud catches up in background)
                update_global_stage(st.session_state.stage)
                
                # 3. Send Email
                send_notification(current["title"])
                
                st.rerun()
            else:
                st.error("INCORRECT PASSWORD.")
