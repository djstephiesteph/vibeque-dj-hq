import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="VibeQue DJ HQ", layout="wide")
st.title("🎧 VibeQue DJ HQ — You Run the Vibe")

# --- AUTHENTICATION ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# --- LOAD SHEET ---
SHEET_ID = "1JkgaBwbmy7iT8iuEaekEIhWMyc4Su35GnFiRqw2pS9Y"
SHEET_NAME = "Request Log"
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- PROCESS ---
# Convert Timestamp to datetime object
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')

# Add Request Type (Pre-Request vs On-Demand)
event_cutoff = datetime.now().replace(hour=18, minute=30, second=0, microsecond=0)
df["Request Type"] = df["Timestamp"].apply(lambda t: "Pre-Request" if t < event_cutoff else "On-Demand")

# Live Sync Badge
st.markdown("✅ **Live Sync OK**")
st.caption(f"Last Sync: {datetime.now().strftime('%A, %B %d, %I:%M %p')}")

# FILTERS
with st.sidebar:
    st.header("🔍 Filters")
    show_only_unplayed = st.checkbox("Only show unplayed")
    selected_user = st.selectbox("Filter by user", ["All"] + sorted(df["User"].dropna().unique().tolist()))

# Apply Filters
if show_only_unplayed:
    df = df[df["Status"] != "Played"]

if selected_user != "All":
    df = df[df["User"] == selected_user]

# DISPLAY TABLE
st.subheader("🎶 Request Queue")

if df.empty:
    st.info("No current requests match the selected filters.")
else:
    styled_df = df[["Timestamp", "User", "Song", "Line Dance Name", "Mood", "Dance Level", "Request Type"]]
    styled_df.index = range(1, len(styled_df) + 1)
    st.dataframe(styled_df, use_container_width=True, height=500)

# FOOTER
st.markdown("---")
st.caption("Powered by VibeQue 💃🏾🎶 | Admin View Only | #LETSWORK")
