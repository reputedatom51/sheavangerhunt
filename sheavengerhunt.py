import streamlit as st
import smtplib
from email.mime.text import MIMEText
import extra_streamlit_components as stx
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="The Invasion", page_icon="🏆", layout="centered")

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stTextInput > div > div > input { 
        text-align: center; text-transform: uppercase; 
        font-weight: bold; font-size: 20px; 
        background-color: #262730; color: white; 
    }
    h1 { text-align: center; color: #d32f2f; border-bottom: 2px solid #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EMAIL NOTIFICATION FUNCTION ---
def send_notification(stage_name):
    if "email" in st.secrets:
        try:
            sender_email = st.secrets["email"]["username"]
            sender_password = st.secrets["email"]["password"]
            recipients = st.secrets["email"]["recipients"]
            
            subject = f"🚨 UPDATE: He cleared {stage_name}!"
            body = f"The RD has successfully entered the password for {stage_name}. He is moving to the next location."
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipients)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipients, msg.as_string())
        except Exception as e:
            print(f"Email failed: {e}")

# --- 4. GAME DATA (STAGES) ---
stages = [
    {
        "title": "THE CHALLENGE",
        "password": "ACCEPT",
        "clue": "**ATTENTION RD:**\n\nYour Championship Title has been vacated. It is currently held in enemy territory.\n\nTo reclaim it, you must run the Gauntlet.\n\n*Type 'ACCEPT' to begin.*"
    },
    {
        "title": "MATCH 1: THE TRAINING",
        "password": "IRON", 
        "clue": "Champions aren't born, they're built.\n\nGo to the **Campus Gym**.\nFind the treadmill that leads to nowhere.\nThe password is taped beneath the console."
    },
    {
        "title": "MATCH 2: THE MOLE",
        "password": "TRAITOR", 
        "clue": "I have a spy on the inside.\n\nFind the resident in **Your Building** who lived in **Room 204** two years ago.\nAsk them for the code."
    },
    {
        "title": "MATCH 3: THE TAPE STUDY",
        "password": "KAYFABE", 
        "clue": "To beat your opponent, you must study history.\n\nGo to the **Library**.\nFind the book: *'Leadership 101'*.\nThe code is on a bookmark inside."
    },
    {
        "title": "MATCH 4: MANAGEMENT",
        "password": "BOSS", 
        "clue": "This match requires administrative approval.\n\nGo to **[MY DORM NAME]**.\nFind the General Manager (The RD).\nConvince them to give you the code."
    },
    {
        "title": "MAIN EVENT: THE GHOST",
        "password": "INTERIM", 
        "clue": "One final obstacle stands between you and the Title.\n\n**'It is with a former RA.'**\n\n*(Hint: Not all who serve stay for the spring.)*"
    }
]

# --- 5. STATE MANAGEMENT (COOKIES) ---

# Initialize the Cookie Manager
cookie_manager = stx.CookieManager()

# Give the manager a moment to load the cookie from the browser
time.sleep(0.1)
cookie_stage = cookie_manager.get(cookie="scavenger_level")

# Initialize Session State using the Cookie if it exists
if "stage" not in st.session_state:
    if cookie_stage:
        st.session_state.stage = int(cookie_stage)
    else:
        st.session_state.stage = 0

# --- 6. DISPLAY ---
progress = st.session_state.stage / len(stages)
st.progress(progress)
st.title("THE INVASION")

# WIN SCREEN
if st.session_state.stage >= len(stages):
    st.balloons()
    st.success("🏆 NEW CHAMPION CROWNED! 🏆")
    st.markdown("""
    ### YOU HAVE DEFEATED THE STABLE.
    The Title Belt is waiting for you at:
    **[INSERT FINAL LOCATION HERE]**
    """)
    if st.button("Reset Game"):
        cookie_manager.delete("scavenger_level")
        st.session_state.stage = 0
        st.rerun()

# GAME SCREEN
else:
    current_data = stages[st.session_state.stage]
    st.subheader(current_data["title"])
    st.markdown(current_data["clue"])
    
    with st.form(key=f"stage_{st.session_state.stage}"):
        user_input = st.text_input("ENTER PASSWORD")
        submit_button = st.form_submit_button("SUBMIT")
        
        if submit_button:
            # CHEAT CODE (In case cookies fail, he can type this to skip)
            # Format: JUMP3 (Jumps to level 3)
            if user_input.upper().startswith("JUMP"):
                try:
                    level_jump = int(user_input[-1])
                    st.session_state.stage = level_jump
                    cookie_manager.set("scavenger_level", level_jump, expires_at=None)
                    st.rerun()
                except:
                    pass

            # NORMAL PASSWORD CHECK
            if user_input.strip().upper() == current_data["password"]:
                # 1. Update State
                st.session_state.stage += 1
                
                # 2. Update Cookie (This saves it to his phone)
                cookie_manager.set("scavenger_level", st.session_state.stage, expires_at=None)
                
                # 3. Send Email
                send_notification(current_data["title"])
                
                # 4. Rerun to refresh the page
                st.rerun()
            else:
                st.error("INCORRECT PASSWORD.")
