import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration & Security
st.set_page_config(page_title="Admin - DCPO Management", 
  layout="wide", 
  page_icon="🛡️")

# Custom CHD-CAR Forest Green & Gold Styling
st.markdown("""
    <style>
    [data-testid="stHeader"] { background-color: #006400; }
    
    div.stButton > button:first-child {
        background-color: #006400; color: white; border-radius: 4px;
        border: none; padding: 0.5rem 1rem; font-weight: 600;
        transition: all 0.3s ease;
    }

    div.stButton > button:first-child:hover {
        background-color: #FFD700; color: #004d00;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    h1, h2, h3 {
        color: #006400 !important; border-left: 6px solid #FFD700;
        padding-left: 15px; font-family: 'Segoe UI', sans-serif;
    }

    [data-testid="stSidebar"] { border-right: 3px solid #FFD700; }

    [data-testid="stMetricValue"] { color: #006400; font-weight: bold; }

    div[data-testid="stExpander"], .stForm {
        border: 1px solid #006400; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Security Check
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please login via the main page first.")
    st.stop()

if str(st.session_state.user_info['UserType']).lower() != 'admin':
    st.error("Unauthorized Access: Admins only.")
    st.stop()

# 2. Setup Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_dcpo_data():
    return conn.read(worksheet="dcpo", ttl=0)

# --- 3. MODAL DIALOGS ---

@st.dialog("➕ Add New DCPO Record")
def add_modal(full_df):
    st.subheader("New Personnel Order Details")
    auto_id = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    current_uid = st.session_state.user_info['UserId']
    curr_year = datetime.now().year
    
    # Auto-increment logic for PersonnelOrderNo
    try:
        year_filter = full_df['PersonnelOrderNo'].astype(str).str.startswith(str(curr_year))
        year_records = full_df[year_filter]
        if not year_records.empty:
            last_val = str(year_records['PersonnelOrderNo'].iloc[-1])
            last_seq = int(last_val.split('-')[1])
            new_seq = f"{curr_year}-{str(last_seq + 1).zfill(3)}"
        else:
            new_seq = f"{curr_year}-001"
    except:
        new_seq = f"{curr_year}-001"

    with st.form("add_new_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Record ID (Auto)", value=auto_id, disabled=True)
            date_prepared = st.date_input("Date Prepared", value=datetime.now())
            date_travel = st.date_input("Date of Travel")
            status = st.selectbox("Status", options=["done", "pending"], index=0)
        with col2:
            st.text_input("Order No (Auto)", value=new_seq, disabled=True)
            name_org = st.text_input("Name/Organization")
            place_travel = st.text_input("Place of Travel")
        
        # New Column Added Here
        soft_copy_link = st.text_input("Soft Copy Link (URL)", placeholder="https://drive.google.com/...")
        purpose = st.text_area("Purpose of Travel")
        
        if st.form_submit_button("Submit Record", use_container_width=True, type="primary"):
            if not name_org or not place_travel:
                st.error("Please fill in required fields.")
            else:
                new_row = {
                    "RecordID": auto_id, "UserId": current_uid, "PersonnelOrderNo": new_seq,
                    "DatePrepared": str(date_prepared), "NameOrganization": name_org,
                    "DateOfTravel": str(date_travel), "PlaceOfTravel": place_travel,
                    "Purpose": purpose, "Status": status, "SoftCopyLink": soft_copy_link
                }
                updated_df = pd.concat([full_df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="dcpo", data=updated_df)
                st.success("New record added!")
                st.rerun()

@st.dialog("📋 Full Record Details")
def details_modal(row_data):
    st.write(f"### Details for {row_data['PersonnelOrderNo']}")
    st.divider()
    
    # Display details
    for col, val in row_data.items():
        if col == "SoftCopyLink" and pd.notna(val) and str(val).startswith("http"):
            st.markdown(f"**{col}:**")
            st.link_button("📂 View Document", val)
        else:
            st.markdown(f"**{col}:** {val}")
            
    if st.button("Close", use_container_width=True):
        st.rerun()

@st.dialog("📝 Edit Record")
def edit_modal(row_index, current_row, full_df):
    st.write(f"Editing: {current_row['PersonnelOrderNo']}")
    updated = {}
    
    # Using columns for a cleaner edit form
    for col in full_df.columns:
        is_disabled = col in ["RecordID", "UserId"]
        updated[col] = st.text_input(f"{col}", value=str(current_row[col]), disabled=is_disabled)
    
    if st.button("Update Google Sheet", type="primary", use_container_width=True):
        full_df.loc[row_index] = updated
        conn.update(worksheet="dcpo", data=full_df)
        st.success("Successfully updated!")
        st.rerun()

@st.dialog("⚠️ Confirm Delete")
def delete_modal(row_index, full_df):
    st.warning("Are you sure? This will permanently remove the record from the database.")
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        conn.update(worksheet="dcpo", data=full_df.drop(row_index))
        st.rerun()

# --- 4. MAIN UI ---
st.title("🛡️ Admin: DCPO Records Management")

try:
    df = get_dcpo_data()
    curr_year = datetime.now().year

    # --- LATEST DCPO CARD ---
    year_data = df[df['PersonnelOrderNo'].astype(str).str.startswith(str(curr_year))]
    
    with st.container(border=True):
        st.subheader(f"✨ Latest DCPO for {curr_year}")
        if not year_data.empty:
            last_record = year_data.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Order No", last_record['PersonnelOrderNo'])
            c2.metric("Organization", (str(last_record['NameOrganization'])[:15] + "...") if len(str(last_record['NameOrganization'])) > 15 else last_record['NameOrganization'])
            c3.metric("Date", str(last_record['DateOfTravel']))
            c4.metric("Status", last_record['Status'].upper())
        else:
            st.info(f"No records found for the year {curr_year}.")

    # --- TOOLBAR ---
    with st.container(border=True):
        c_search, c_add, c_refresh = st.columns([3, 1, 1])
        with c_search:
            search = st.text_input("Search", placeholder="🔍 Search records...", label_visibility="collapsed").lower()
        with c_add:
            if st.button("➕ Add New", use_container_width=True, type="primary"):
                add_modal(df)
        with c_refresh:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

    # Filtering logic
    display_df = df[df.astype(str).apply(lambda x: x.str.lower().str.contains(search)).any(axis=1)] if search else df

    st.write(f"**Total Records Found:** {len(display_df)}")

    # Adjusted selection to include the SoftCopyLink column (Assuming it's at the end)
    # PersonnelOrderNo, DatePrepared, NameOrganization, SoftCopyLink
    view_df = display_df[['PersonnelOrderNo', 'DatePrepared', 'NameOrganization', 'SoftCopyLink']]

    # Scrollable Dataframe
    event = st.dataframe(
        view_df,
        use_container_width=True,
        hide_index=False,
        selection_mode="single-row",
        on_select="rerun",
        height=350,
        column_config={
            "SoftCopyLink": st.column_config.LinkColumn("Document", display_text="Open 📄")
        }
    )

    # --- 5. ACTION BAR ---
    selected_indices = event.selection.rows
    if selected_indices:
        actual_index = display_df.index[selected_indices[0]]
        selected_row_data = display_df.loc[actual_index]
        
        st.success(f"Selected: **{selected_row_data['PersonnelOrderNo']}**")
        
        b1, b2, b3, _ = st.columns([1, 1, 1, 5])
        with b1:
            if st.button("📝 Edit", use_container_width=True):
                edit_modal(actual_index, selected_row_data, df)
        with b2:
            if st.button("🗑️ Delete", use_container_width=True):
                delete_modal(actual_index, df)
        with b3:
            if st.button("🔍 Details", use_container_width=True):
                details_modal(selected_row_data)
    else:
        st.info("💡 Select a row in the table above to interact with it.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")

# SIDEBAR
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/2a/DOH_PH_new_logo.svg", width=80)    
    st.write(f"Logged in: **{st.session_state.user_info['FullName']}**")
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()
        
# --- FOOTER SECTION ---
current_year = datetime.now().year # This pulls 2026 automatically

st.divider()
st.markdown(
    f"""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p style="margin: 0;"><strong>Department of Health - Baguio & Benguet - Cordillera</strong></p>
        <p style="margin: 0; color: #888; font-size: 0.75rem;">DCPO Tracker System v1.0 | © {current_year}</p>
    </div>
    """,
    unsafe_allow_html=True
)