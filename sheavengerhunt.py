import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Invasion",
    page_icon="🏆",
    layout="centered"
)

# --- CUSTOM CSS (The "Wrestling/Dark" Look) ---
st.markdown("""
    <style>
    /* Force Dark Theme vibes */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stTextInput > div > div > input {
        text-align: center;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 20px;
    }
    h1 {
        text-align: center; 
        color: #d32f2f; /* WWE Red */
        text-transform: uppercase;
        border-bottom: 2px solid #d32f2f;
    }
    .success-msg {
        color: #4caf50;
        font-weight: bold;
        text-align: center;
    }
    .error-msg {
        color: #ff5252;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE (To remember his progress) ---
if 'stage' not in st.session_state:
    st.session_state.stage = 0

# --- THE GAME DATA (Passwords & Clues) ---
# UPDATE THESE PASSWORDS TO YOUR REAL ONES
stages = [
    {
        "title": "THE CHALLENGE",
        "clue": """
        **ATTENTION RD:**
        
        Your Championship Title has been vacated. It is currently held in enemy territory.
        
        To reclaim it, you must run the Gauntlet. Defeat my opponents, collect the passwords, and prove you are the True Champion.
        
        *Type 'ACCEPT' to begin.*
        """,
        "password": "ACCEPT",
        "hint": "Type ACCEPT to start."
    },
    {
        "title": "MATCH 1: THE TRAINING",
        "clue": """
        Champions aren't born, they're built.
        
        Go to the **Campus Gym**.
        Find the treadmill that leads to nowhere.
        The password is taped beneath the console.
        """,
        "password": "IRON",
        "hint": "Go to the Gym."
    },
    {
        "title": "MATCH 2: THE MOLE",
        "clue": """
        I have a spy on the inside.
        
        Find the resident in **Your Building** who lived in Room 204 two years ago.
        Ask them for the code.
        """,
        "password": "TRAITOR",
        "hint": "Find the student."
    },
    {
        "title": "MATCH 3: THE TAPE STUDY",
        "clue": """
        To beat your opponent, you must study history.
        
        Go to the **Library**.
        Find the book: *"Leadership 101"*.
        The code is on a bookmark inside.
        """,
        "password": "KAYFABE",
        "hint": "Go to the Library."
    },
    {
        "title": "MATCH 4: MANAGEMENT",
        "clue": """
        This match requires administrative approval.
        
        Go to **[My Dorm Name]**.
        Find the General Manager (The RD).
        Convince them to give you the code.
        """,
        "password": "BOSS",
        "hint": "Find my RD."
    },
    {
        "title": "MAIN EVENT: THE GHOST",
        "clue": """
        One final obstacle stands between you and the Title.
        
        **"It is with a former RA."**
        
        *(Hint: Not all who serve stay for the spring.)*
        """,
        "password": "INTERIM",
        "hint": "Find the J-Term RA."
    }
]

# --- GAME LOGIC ---

# Progress Bar
progress = st.session_state.stage / len(stages)
st.progress(progress)

# Header
st.title("THE INVASION")

# Check if game is finished
if st.session_state.stage >= len(stages):
    st.balloons()
    st.success("🏆 NEW CHAMPION CROWNED! 🏆")
    st.markdown("""
    ### YOU HAVE DEFEATED THE STABLE.
    
    The Title Belt is waiting for you at:
    **[INSERT FINAL LOCATION / APARTMENT NUMBER]**
    
    *Come claim your prize.*
    """)
    if st.button("Reset Game (Debug)"):
        st.session_state.stage = 0
        st.rerun()

else:
    # Get current stage data
    current_data = stages[st.session_state.stage]
    
    st.subheader(current_data["title"])
    st.markdown(current_data["clue"])
    
    # Input Form
    with st.form(key=f"stage_{st.session_state.stage}"):
        user_input = st.text_input("ENTER PASSWORD", key="user_input")
        submit_button = st.form_submit_button(label="SUBMIT")
        
        if submit_button:
            # Check Password (case insensitive)
            if user_input.strip().upper() == current_data["password"]:
                st.session_state.stage += 1
                st.rerun()
            else:
                st.error("INCORRECT PASSWORD. TRY AGAIN.")