import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Data Extraction Test", layout="wide")

st.title("🔍 DCPO Connection Diagnostic")
st.write("This script tests if the Service Account can see your Google Sheet.")

# 1. Initialize Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.success("✅ Connection Object Created")
except Exception as e:
    st.error(f"❌ Failed to initialize connection: {e}")
    st.stop()

# 2. Try to Read the 'dcpo' Sheet
st.subheader("Attempting to read 'dcpo' worksheet...")

try:
    # We use ttl=0 to ensure we aren't seeing old cached 'empty' results
    df = conn.read(worksheet="dcpo", ttl=0)
    
    if df is not None:
        st.write(f"📊 **Rows Found:** {len(df)}")
        st.write(f"📋 **Columns Found:** {df.columns.tolist()}")
        
        if not df.empty:
            st.write("### ⬇️ Raw Data Preview")
            st.dataframe(df)
        else:
            st.warning("⚠️ The sheet was found, but it appears to be empty (no data rows).")
            st.info("Check if your data starts on Row 2 (with Headers in Row 1).")
    else:
        st.error("❌ The returned data is 'None'. Check worksheet name spelling.")

except Exception as e:
    st.error("❌ Extraction Failed!")
    st.exception(e)
    
    st.markdown("""
    ### 🛠️ Common Fixes for this Error:
    1. **Share Permissions:** Ensure the `client_email` from your `secrets.toml` is added as an **Editor** on the Google Sheet.
    2. **Tab Name:** Ensure the tab at the bottom of your Google Sheet is named exactly **dcpo** (lowercase, no spaces).
    3. **Private Key:** Ensure the `private_key` in your `secrets.toml` includes the `\n` characters and the `-----BEGIN...` / `-----END...` lines.
    """)

# 3. Simple Button to clear cache and retry
if st.button("♻️ Clear Cache and Retry"):
    st.cache_data.clear()
    st.rerun()