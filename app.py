import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib  # Added for secure token generation

# 1. Page Configuration
st.set_page_config(
    page_title="DCPO Tracker System Login", 
    page_icon="🔒", 
    layout="centered"
)

# Custom DOH Cordillera Styling
st.markdown("""
    <style>
    [data-testid="stHeader"] { background-color: #006641; }
    div.stButton > button:first-child {
        background-color: #006641; color: white; border-radius: 5px;
        border: none; font-weight: 600;
    }
    div.stButton > button:first-child:hover {
        background-color: #E6B800; color: #006641;
    }
    [data-testid="stMetricValue"] { color: #006641; }
    h1 {
        color: #006641; border-bottom: 3px solid #E6B800;
        padding-bottom: 10px;
    }
    [data-testid="stSidebar"] { border-right: 2px solid #E6B800; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY UTILITIES ---
SALT = "CHD_CAR_INTERNAL_SECRET_2026" # Change this to any random string

def make_hash(user_id):
    """Encodes the UserId into a secure hex string."""
    return hashlib.sha256(f"{user_id}{SALT}".encode()).hexdigest()

# 3. Setup Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_user_by_token(token):
    """Attempts to find a user in the database matching the URL hash."""
    try:
        df = conn.read(worksheet="users", ttl=0)
        for _, row in df.iterrows():
            if make_hash(str(row['UserId'])) == token:
                return row
        return None
    except:
        return None

def login_user(username, password):
    try:
        df = conn.read(worksheet="users", ttl=0)
        df['UserName'] = df['UserName'].astype(str).str.strip()
        df['Password'] = df['Password'].astype(str).str.strip()
        user_record = df[(df['UserName'] == username) & (df['Password'] == password)]
        if not user_record.empty:
            return user_record.iloc[0]
        return None
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- 4. INITIALIZE SESSION & HANDLE REFRESH (F5) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# AUTO-LOGIN LOGIC: If session is lost but URL has a token, restore session
url_token = st.query_params.get("st_token")
if not st.session_state.logged_in and url_token:
    user = get_user_by_token(url_token)
    if user is not None:
        st.session_state.logged_in = True
        st.session_state.user_info = user

# --- 5. LOGIN CONTENT ---
def login_screen():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/2a/DOH_PH_new_logo.svg", width=80)
    with c2:
        st.title("DCPO Tracker System")
    
    st.subheader("🛡️ Secure Login")
    
    with st.form("login_form"):
        username_input = st.text_input("Username", placeholder="Enter your username")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)

        if submit_button:
            if username_input and password_input:
                user = login_user(username_input, password_input)
                if user is not None:
                    st.session_state.logged_in = True
                    st.session_state.user_info = user
                    
                    # Generate hash and save to URL query params
                    token = make_hash(str(user['UserId']))
                    st.query_params["st_token"] = token
                    
                    st.success(f"Welcome, {user['FullName']}!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password.")
            else:
                st.warning("Please enter both a username and a password.")

    st.write("---")
    if st.button("🌐 Continue as Guest (View Only)", use_container_width=True):
        st.switch_page(guest_page) 

    st.markdown("---")
    st.caption("DCPO Records Management System v1.0 | CHD-CAR")

# --- 6. NAVIGATION SETUP ---
login_page = st.Page(login_screen, title="Login", icon="🔐", default=True)
admin_page = st.Page("pages/adminPage.py", title="Admin", icon="🛡️")
guest_page = st.Page("pages/guestPage.py", title="Guest", icon="📖")

# Custom logout function to clear URL params
def logout():
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.query_params.clear() # Removes the token from the URL
    st.rerun()

if st.session_state.logged_in:
    user_role = str(st.session_state.user_info['UserType']).lower()
    
    # Inject a logout button in sidebar for all logged-in users
    with st.sidebar:
        if st.button("Logout", use_container_width=True):
            logout()
            
    if user_role == 'admin':
        pg = st.navigation({
            "Management": [admin_page],
            "Public View": [guest_page]
        })
    else:
        pg = st.navigation([guest_page])
else:
    pg = st.navigation([login_page, guest_page])

# 7. Run the Navigation
pg.run()