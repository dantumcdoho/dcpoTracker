import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="DCPO Tracker Records", layout="wide", page_icon="📖")

# --- CHD-CAR THEME CSS ---
st.markdown("""
    <style>
    /* Top Header Bar */
    [data-testid="stHeader"] {
        background-color: #006400;
    }
    
    /* Forest Green Buttons */
    div.stButton > button:first-child {
        background-color: #006400; color: white; border-radius: 4px;
        border: none; font-weight: 600; transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #FFD700; color: #004d00;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Section Headers */
    h1, h2, h3 {
        color: #006400 !important; border-left: 6px solid #FFD700;
        padding-left: 15px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    [data-testid="stSidebar"] { border-right: 3px solid #FFD700; }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #006400;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_dcpo_data():
    # ttl=300 keeps data cached for 5 minutes for performance
    return conn.read(worksheet="dcpo", ttl=300)

@st.dialog("📋 Full Record Details")
def view_modal(row_data):
    st.write(f"### Details for {row_data['PersonnelOrderNo']}")
    st.divider()
    
    # Display all data except the link in a table
    main_details = row_data.drop("SoftCopyLink")
    st.table(main_details.astype(str))
    
    # Special Button for the Soft Copy Link
    link = row_data.get('SoftCopyLink', '')
    if pd.notna(link) and str(link).startswith("http"):
        st.link_button("📂 View Shared Soft Copy", link, use_container_width=True)
    else:
        st.info("No soft copy link available for this record.")
        
    if st.button("Close", use_container_width=True):
        st.rerun()

# --- MAIN UI ---
st.title("📖 DCPO Public Records")
st.info("Notice: You are in View-Only mode.")

try:
    df = get_dcpo_data()
    curr_year = datetime.now().year

    # --- 3. LATEST RECORD CARD ---
    year_data = df[df['PersonnelOrderNo'].astype(str).str.startswith(str(curr_year))]
    
    with st.container(border=True):
        st.subheader(f"✨ Latest DCPO for {curr_year}")
        if not year_data.empty:
            last_record = year_data.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Order No", last_record['PersonnelOrderNo'])
            c2.metric("Organization", (str(last_record['NameOrganization'])[:15] + "...") if len(str(last_record['NameOrganization'])) > 15 else last_record['NameOrganization'])
            c3.metric("Date", str(last_record['DateOfTravel']))
            c4.metric("Status", str(last_record['Status']).upper())
        else:
            st.info(f"No records found for {curr_year}.")

    # --- 4. SEARCH & REFRESH ---
    with st.container(border=True):
        c_search, c_refresh = st.columns([4, 1])
        with c_search:
            search = st.text_input("Search", placeholder="🔍 Search by Order No, Org, or Venue...", label_visibility="collapsed").lower()
        with c_refresh:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

    # Filtering logic
    display_df = df[df.astype(str).apply(lambda x: x.str.lower().str.contains(search)).any(axis=1)] if search else df

    # --- 5. DATA FRAME DISPLAY ---
    st.write(f"**Total Records:** {len(display_df)}")
    
    # We display relevant columns including the SoftCopyLink
    # Ensure your Sheet has these headers: PersonnelOrderNo, DatePrepared, NameOrganization, DateOfTravel, Status, SoftCopyLink
    view_columns = ['PersonnelOrderNo', 'DateOfTravel', 'NameOrganization', 'Status', 'SoftCopyLink']
    
    # Safely select columns that exist in the dataframe
    available_cols = [c for c in view_columns if c in display_df.columns]
    view_df = display_df[available_cols]

    # Configuration for the table
    event = st.dataframe(
        view_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        height=450,
        column_config={
            "PersonnelOrderNo": "Order No",
            "DateOfTravel": "Travel Date",
            "NameOrganization": "Organization",
            "Status": st.column_config.TextColumn("Status"),
            "SoftCopyLink": st.column_config.LinkColumn(
                "Document", 
                display_text="Open 📄", 
                help="Click to view the soft copy of the Personnel Order"
            )
        }
    )

    # --- 6. ACTION FOR SELECTED ROW ---
    selected_indices = event.selection.rows
    if selected_indices:
        # Get the actual data from the filtered dataframe
        actual_index = display_df.index[selected_indices[0]]
        selected_row_data = display_df.loc[actual_index]
        
        if st.button(f"🔍 View Full Details for {selected_row_data['PersonnelOrderNo']}", use_container_width=True):
            view_modal(selected_row_data)
    else:
        st.caption("💡 Select a row in the table above to view complete details.")

except Exception as e:
    st.error(f"Error loading records: {e}")
        
# SIDEBAR
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/2a/DOH_PH_new_logo.svg", width=80)
    st.write("**CHD-CAR DCPO Tracker**")
    st.divider()
        
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