import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE CONFIG ---
st.set_page_config(page_title="VibeQue DJ HQ", layout="wide")
st.title("🎧 VibeQue DJ HQ — You Run the Vibe")

# --- AUTH ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- LOAD SHEET ---
SHEET_ID = "1JkgaBwbmy7iT8iuEaekEIhWMyc4Su35GnFiRqw2pS9Y"
SHEET_NAME = "Request Log"
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- CLEAN & PROCESS ---
df.columns = df.columns.str.strip()  # Strip whitespace from column names

# Validate required columns
required_cols = ["Timestamp", "Song", "Artist", "Line Dance Name", "Mood", "Dance Level", "Submitted By", "Status", "Submission Type"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"❌ Missing columns: {', '.join(missing_cols)}. Please check your Google Sheet.")
    st.stop()

# Timestamp formatting
try:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
except Exception as e:
    st.error("⚠️ Failed to parse Timestamp column.")
    st.stop()

# Determine Request Type
event_cutoff = datetime.now().replace(hour=18, minute=30, second=0, microsecond=0)
df["Request Type"] = df["Timestamp"].apply(lambda t: "Pre-Request" if pd.notnull(t) and t < event_cutoff else "On-Demand")

# --- BADGES ---
st.success("✅ Live Sync OK")
st.caption(f"🕒 Last Sync: {datetime.now().strftime('%A, %B %d, %I:%M %p')}")

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🔍 Filters")
    show_only_unplayed = st.checkbox("Only show unplayed")
    selected_user = st.selectbox("Filter by submitter", ["All"] + sorted(df["Submitted By"].dropna().unique().tolist()))

# --- FILTER LOGIC ---
if show_only_unplayed:
    df = df[df["Status"] != "Played"]

if selected_user != "All":
    df = df[df["Submitted By"] == selected_user]

# --- DISPLAY DYNAMIC CARDS ---
st.subheader("📀 Current Request Queue")
if df.empty:
    st.info("No matching song requests right now.")
else:
    for _, row in df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**🎵 Song:** {row['Song']}")
                st.markdown(f"**🕺🏾 Dance:** {row['Line Dance Name']}")
                st.markdown(f"**🎤 Artist:** {row['Artist']}")
            with col2:
                st.markdown(f"**🧠 Mood:** {row['Mood']}")
                st.markdown(f"**💃🏾 Level:** {row['Dance Level']}")
                st.markdown(f"**📨 Submitted By:** {row['Submitted By']}")
            with col3:
                st.markdown(f"**🕒** {row['Timestamp'].strftime('%I:%M %p') if pd.notnull(row['Timestamp']) else 'N/A'}")
                st.markdown(f"**⚙️ Type:** {row['Request Type']}")
                st.markdown(f"**📍Status:** {row['Status']}")
            st.markdown("---")

# --- FOOTER ---
st.markdown("---")
st.caption("Admin View • Powered by VibeQue 🎶 | #LETSWORK")
