import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="DCPO Tracker System Login", 
    page_icon="🔒", 
    layout="centered"
)

# Custom DOH Cordillera Styling
st.markdown("""
    <style>
    /* Header background color */
    [data-testid="stHeader"] {
        background-color: #006641;
    }
    
    /* Customize the 'Primary' buttons */
    div.stButton > button:first-child {
        background-color: #006641;
        color: white;
        border-radius: 5px;
        border: none;
        font-weight: 600;
    }

    /* Hover effect for buttons */
    div.stButton > button:first-child:hover {
        background-color: #E6B800; /* DOH Gold/Yellow */
        color: #006641;
    }

    /* Styling the Metric cards */
    [data-testid="stMetricValue"] {
        color: #006641;
    }
    
    /* Main Title Color - Fixed double ## here */
    h1 {
        color: #006641;
        border-bottom: 3px solid #E6B800;
        padding-bottom: 10px;
    }
    
    /* Sidebar accent */
    [data-testid="stSidebar"] {
        border-right: 2px solid #E6B800;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# 3. Setup Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

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

# --- 4. DEFINE THE LOGIN PAGE CONTENT ---
def login_screen():
    # Official Header
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

# --- 5. NAVIGATION SETUP ---
login_page = st.Page(login_screen, title="Login", icon="🔐", default=True)
admin_page = st.Page("pages/adminPage.py", title="Admin", icon="🛡️")
guest_page = st.Page("pages/guestPage.py", title="Guest", icon="📖")

if st.session_state.logged_in:
    user_role = str(st.session_state.user_info['UserType']).lower()
    
    if user_role == 'admin':
        pg = st.navigation({
            "Management": [admin_page],
            "Public View": [guest_page]
        })
    else:
        pg = st.navigation([guest_page])
else:
    pg = st.navigation([login_page, guest_page])

# 6. Run the Navigation
pg.run()