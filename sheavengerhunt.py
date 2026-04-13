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
    {"title": "Reclaim Your Title", "key": "intro", "clue": "Find 6 Opponents to Earn Your Title Match. Type Accept to Continue"},
    {"title": "MATCH 1", "key": "DJ", "clue": "Start by finding Bethel’s most popular tag team, maybe known as DJ."},
    {"title": "MATCH 2", "key": "Mikiah", "clue": "Next find certain individual who watches your kids and now resides over plenty of her own “children” on the hill might"},
    {"title": "MATCH 3", "key": "Kyle", "clue": "Now find a former L3 resident who has climbed in ranks, but dropped in floors."},
    {"title": "MATCH 4", "key": "Tyler", "clue": "Next find a 3-time RA, yet younger than the seniors."},
    {"title": "Match 5", "key": "Dylan", "clue": "Find your Solo Sikoa."},
    {"title": "Match 6", "key": "Lexi", "clue": "Find our favorite formerly blonde friend who broke her foot falling down a single step."},
    {"title": "Match 7", "key": "Sarah", "clue": "Find a former Lissner RA but dig deep to figure out who they are."},
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
    st.success("The Final Boss")
    st.write(f"Your Title Match is scheduled for Sunday. Be prepared, my tribal chief.")
    
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
