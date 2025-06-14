import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE SETUP ---
st.set_page_config(page_title="VibeQue DJ HQ", layout="wide")
st.title("🎧 VibeQue DJ HQ — You Run the Vibe")

# --- GOOGLE AUTH ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- LOAD SHEET ---
SHEET_ID = "1JkgaBwbmy7iT8iuEaekEIhWMyc4Su35GnFiRqw2pS9Y"
SHEET_NAME = "Request Log"  # Adjust this if your sheet/tab has a different name
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = worksheet.get_all_records()

df = pd.DataFrame(data)
df.columns = [str(col).strip() for col in df.columns]
st.write("Columns in sheet:", df.columns.tolist())  # ✅ Debug


# --- DEBUG COLUMNS ---
st.write("🧾 Sheet Columns Detected:", df.columns.tolist())

# --- CLEAN & PROCESS ---
# Rename columns if needed
df.columns = [col.strip() for col in df.columns]

# Fix Timestamp
if "Timestamp" in df.columns:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
else:
    st.error("❌ 'Timestamp' column not found. Please check your sheet.")
    st.stop()

# Add Request Type (Pre-Request vs On-Demand)
event_cutoff = datetime.now().replace(hour=18, minute=30, second=0, microsecond=0)
df["Request Type"] = df["Timestamp"].apply(lambda t: "Pre-Request" if t < event_cutoff else "On-Demand")

# --- LIVE SYNC ---
st.markdown("✅ **Live Sync OK**")
st.caption(f"Last Sync: {datetime.now().strftime('%A, %B %d, %I:%M %p')}")

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🔍 Filters")
    show_only_unplayed = st.checkbox("Only show unplayed", value=True)

    if "Submitted By" in df.columns:
        selected_user = st.selectbox("Filter by requestor", ["All"] + sorted(df["Submitted By"].dropna().unique().tolist()))
    else:
        selected_user = "All"

# --- APPLY FILTERS ---
if show_only_unplayed and "Status" in df.columns:
    df = df[df["Status"].str.lower() != "played"]

if selected_user != "All" and "Submitted By" in df.columns:
    df = df[df["Submitted By"] == selected_user]

# --- DISPLAY TABLE ---
st.subheader("🎶 Request Queue")

if df.empty:
    st.info("No current requests match your filters.")
else:
    display_cols = ["Timestamp", "Submitted By", "Song", "Line Dance Name", "Mood", "Dance Level", "Request Type"]
    display_cols = [col for col in display_cols if col in df.columns]
    df.index = range(1, len(df) + 1)
    st.dataframe(df[display_cols], use_container_width=True, height=500)

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by VibeQue 💃🏾🎶 | Admin View Only | #LETSWORK")
