import streamlit as st
import smtplib
from email.mime.text import MIMEText

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Invasion", 
    page_icon="🏆", 
    layout="centered"
)

# --- 2. CUSTOM CSS (Dark Mode & Wrestling Theme) ---
st.markdown("""
    <style>
    /* Dark Theme Background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    /* Input Box Styling */
    .stTextInput > div > div > input {
        text-align: center;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 20px;
        background-color: #262730;
        color: white;
    }
    /* Header Styling */
    h1 {
        text-align: center; 
        color: #d32f2f; /* WWE Red */
        text-transform: uppercase;
        border-bottom: 2px solid #d32f2f;
        padding-bottom: 10px;
    }
    /* Button Styling */
    .stButton > button {
        width: 100%;
        background-color: #d32f2f;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #b71c1c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EMAIL NOTIFICATION FUNCTION ---
def send_notification(stage_name):
    # Only runs if you have set up your secrets correctly
    if "email" in st.secrets:
        try:
            sender_email = st.secrets["email"]["username"]
            sender_password = st.secrets["email"]["password"]
            recipients = st.secrets["email"]["recipients"] # This is a list ['you', 'buddy']
            
            subject = f"🚨 UPDATE: He cleared {stage_name}!"
            body = f"The RD has successfully entered the password for {stage_name}. He is moving to the next location."
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            # Join list into string for the header: "a@gmail.com, b@gmail.com"
            msg['To'] = ", ".join(recipients)
            
            # Connect to Gmail Server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                # Send to the list of recipients
                server.sendmail(sender_email, recipients, msg.as_string())
                
        except Exception as e:
            print(f"Email failed to send: {e}")

# --- 4. GAME DATA (CLUES & PASSWORDS) ---
# !!! CHANGE EVERYTHING IN THIS LIST !!!
stages = [
    {
        "title": "THE CHALLENGE",
        "password": "ACCEPT", # The password to start the game
        "clue": """
        **ATTENTION RD:**
        
        Your Championship Title has been vacated. It is currently held in enemy territory.
        
        To reclaim it, you must run the Gauntlet. Defeat my opponents, collect the passwords, and prove you are the True Champion.
        
        *Type 'ACCEPT' to begin.*
        """
    },
    {
        "title": "MATCH 1: THE TRAINING",
        "password": "IRON", ### CHANGE THIS to the password hidden in the Gym ###
        "clue": """
        Champions aren't born, they're built.
        
        Go to the **Campus Gym**.
        Find the treadmill that leads to nowhere.
        The password is taped beneath the console.
        """
    },
    {
        "title": "MATCH 2: THE MOLE",
        "password": "TRAITOR", ### CHANGE THIS to what the resident will say ###
        "clue": """
        I have a spy on the inside.
        
        Find the resident in **Your Building** who lived in **Room 204** two years ago.
        Ask them for the code.
        """
    },
    {
        "title": "MATCH 3: THE TAPE STUDY",
        "password": "KAYFABE", ### CHANGE THIS to the word in the book ###
        "clue": """
        To beat your opponent, you must study history.
        
        Go to the **Library**.
        Find the book: *"Leadership 101"*.
        The code is on a bookmark inside.
        """
    },
    {
        "title": "MATCH 4: MANAGEMENT",
        "password": "BOSS", ### CHANGE THIS to what your RD says ###
        "clue": """
        This match requires administrative approval.
        
        Go to **[MY DORM NAME]**.
        Find the General Manager (The RD).
        Convince them to give you the code.
        """
    },
    {
        "title": "MAIN EVENT: THE GHOST",
        "password": "INTERIM", ### CHANGE THIS to the J-Term RA's code ###
        "clue": """
        One final obstacle stands between you and the Title.
        
        **"It is with a former RA."**
        
        *(Hint: Not all who serve stay for the spring.)*
        """
    }
]

# --- 5. GAME LOGIC (AUTO-SAVE) ---

# Check URL for progress (e.g. ?level=2)
params = st.query_params
if "level" in params:
    saved_stage = int(params["level"])
else:
    saved_stage = 0

# Initialize Session State
if "stage" not in st.session_state:
    st.session_state.stage = saved_stage
else:
    # If URL is ahead of session, update session
    if saved_stage > st.session_state.stage:
         st.session_state.stage = saved_stage

# --- 6. DISPLAY ---

# Progress Bar
progress = st.session_state.stage / len(stages)
st.progress(progress)

# Header
st.title("THE INVASION")

# WIN SCREEN
if st.session_state.stage >= len(stages):
    st.balloons()
    st.success("🏆 NEW CHAMPION CROWNED! 🏆")
    st.markdown("""
    ### YOU HAVE DEFEATED THE STABLE.
    
    The Title Belt is waiting for you at:
    **[INSERT FINAL LOCATION HERE]**
    
    *Come claim your prize.*
    """)
    
    # Reset Button (For testing)
    if st.button("Reset Game"):
        st.query_params.clear()
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
            # Check Password (case insensitive)
            if user_input.strip().upper() == current_data["password"]:
                
                # 1. Update State
                st.session_state.stage += 1
                
                # 2. Update URL (Auto-Save)
                st.query_params["level"] = str(st.session_state.stage)
                
                # 3. Send Email
                send_notification(current_data["title"])
                
                st.rerun()
            else:
                st.error("INCORRECT PASSWORD. TRY AGAIN.")
