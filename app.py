import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="VibeQue DJ HQ", layout="wide")
st.title("🎧 VibeQue DJ HQ — You Run the Vibe")

# --- AUTH ---
import json
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
from oauth2client.service_account import ServiceAccountCredentials
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)


# --- LOAD SHEET ---
SHEET_ID = "1JkgaBwbmy7iT8iuEaekEIhWMyc4Su35GnFiRqw2pS9Y"
SHEET_NAME = "Request Log"
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- PROCESSING ---
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
event_cutoff = datetime.now().replace(hour=18, minute=30, second=0, microsecond=0)
df["Request Type"] = df["Timestamp"].apply(lambda t: "Pre-Request" if t < event_cutoff else "On-Demand")

# --- UI BADGES ---
st.markdown("✅ **Live Sync OK**")
st.caption(f"Last Sync: {datetime.now().strftime('%A, %B %d, %I:%M %p')}")

# --- FILTERS ---
with st.sidebar:
    st.header("🔍 Filters")
    show_only_unplayed = st.checkbox("Only show unplayed")
    selected_user = st.selectbox("Filter by user", ["All"] + sorted(df["User"].dropna().unique()))

# --- APPLY FILTERS ---
if show_only_unplayed:
    df = df[df["Status"] != "Played"]
if selected_user != "All":
    df = df[df["User"] == selected_user]

# --- DISPLAY QUEUE ---
st.subheader("🎶 Request Queue")
if df.empty:
    st.info("No requests found for this filter.")
else:
    styled_df = df[["Timestamp", "User", "Song", "Line Dance Name", "Mood", "Dance Level", "Request Type"]]
    styled_df.index = range(1, len(styled_df) + 1)
    st.dataframe(styled_df, use_container_width=True, height=600)

# --- FOOTER ---
st.markdown("---")
st.caption("Admin View | Powered by VibeQue 💃🏾🎶 | #LETSWORK")
