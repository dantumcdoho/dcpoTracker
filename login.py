import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="DCPO Management", layout="wide")

# Establish connection
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data(sheet_name):
    # Using ttl=0 to ensure we don't see old/empty cached data
    return conn.read(worksheet=sheet_name, ttl=0)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None

# --- LOGIN UI ---
if not st.session_state.logged_in:
    st.title("🔐 DCPO System Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                users_df = fetch_data("users")
                # Filter for matching credentials
                user_match = users_df[(users_df['UserName'] == username) & (users_df['Password'] == str(password))]
                
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_match.iloc[0]['UserType']
                    st.session_state.user_id = user_match.iloc[0]['UserId']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- AUTHENTICATED VIEW ---
else:
    # Logout button in the top of the sidebar
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.rerun()
    
    if st.session_state.user_type == "Admin":
        import pages.adminPage as adminPage
        adminPage.show_admin_dashboard(conn)
    else:
        st.title("📋 DCPO Dashboard")
        
        try:
            # Fetch and clean data
            dcpo_df = fetch_data("dcpo")
            dcpo_df = dcpo_df.dropna(how='all') # Removes ghost rows

            if dcpo_df.empty:
                st.warning("No records found in the DCPO sheet.")
            else:
                st.subheader("All DCPO Records")
                
                # NO FILTER APPLIED - SHOWS EVERYTHING DIRECTLY
                st.dataframe(
                    dcpo_df[['PersonnelOrderNo', 'NameOrganization', 'DateOfTravel', 'Status']], 
                    use_container_width=True,
                    hide_index=True
                )
                
                # Separate section for Detail View
                st.markdown("---")
                st.subheader("🔍 View Record Details")
                
                # Selectbox based on the RecordID
                record_ids = dcpo_df['RecordID'].tolist()
                selected_order = st.selectbox("Select a Record ID to see more info:", options=record_ids)
                
                if st.button("Show Details"):
                    details = dcpo_df[dcpo_df['RecordID'] == selected_order].iloc[0]
                    
                    # Create columns for a nice layout
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Personnel Order:** {details['PersonnelOrderNo']}")
                        st.write(f"**Organization:** {details['NameOrganization']}")
                        st.write(f"**Place of Travel:** {details['PlaceOfTravel']}")
                    with c2:
                        st.write(f"**Date of Travel:** {details['DateOfTravel']}")
                        st.write(f"**Purpose:** {details['Purpose']}")
                        st.info(f"**Status:** {details['Status']}")

        except Exception as e:
            st.error(f"Error loading dashboard: {e}")