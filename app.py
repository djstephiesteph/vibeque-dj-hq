import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="🎧 VibeQue DJ HQ", layout="wide")
st.title("🎧 VibeQue DJ HQ — You Run the Vibe")

# --- GOOGLE SHEETS AUTH ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- LOAD DATA ---
SHEET_ID = "1JkgaBwbmy7iT8iuEaekEIhWMyc4Su35GnFiRqw2pS9Y"
SHEET_NAME = "Request Log"
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = worksheet.get_all_records()
df = pd.DataFrame(data)
df.columns = df.columns.str.strip()  # Clean headers

# --- CLEAN & PROCESS ---
if "Timestamp" not in df.columns:
    st.error("❌ 'Timestamp' column not found in sheet.")
    st.stop()

df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

event_cutoff = datetime.now().replace(hour=18, minute=30, second=0, microsecond=0)
df["Request Type"] = df["Timestamp"].apply(lambda t: "Pre-Request" if t < event_cutoff else "On-Demand")

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🔍 Filter Queue")
    show_only_unplayed = st.checkbox("Only show unplayed")
    user_list = sorted(df["Submitted By"].dropna().unique().tolist())
    selected_user = st.selectbox("Filter by requestor", ["All"] + user_list)
    sort_order = st.radio("Sort By", ["Newest", "Oldest"], horizontal=True)

# --- FILTER LOGIC ---
filtered_df = df.copy()
if show_only_unplayed:
    filtered_df = filtered_df[filtered_df["Status"] != "Played"]
if selected_user != "All":
    filtered_df = filtered_df[filtered_df["Submitted By"] == selected_user]
filtered_df = filtered_df.sort_values(by="Timestamp", ascending=(sort_order == "Oldest"))

# --- SYNC INFO ---
st.markdown("✅ **Live Sync OK**")
st.caption(f"Last Sync: {datetime.now().strftime('%A, %B %d • %I:%M %p')}")

# --- DISPLAY CARDS ---
st.subheader("📋 Live Request Queue")

if filtered_df.empty:
    st.warning("No matching requests found.")
else:
    for _, row in filtered_df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style='background:#f5f5f5;padding:15px;border-radius:10px;margin-bottom:10px;
                            box-shadow:0 2px 6px rgba(0,0,0,0.1);'>
                    <h4 style='margin:0;'>🎶 <b>{row['Song']}</b> — {row['Artist']}</h4>
                    <p style='margin:5px 0;'>
                        <b>🕒 Time:</b> {row['Timestamp'].strftime('%I:%M %p') if pd.notnull(row['Timestamp']) else '—'}<br>
                        <b>💃🏾 Dance:</b> {row['Line Dance Name']} &nbsp;&nbsp;
                        <b>📁 Type:</b> {row['Submission Type']} &nbsp;&nbsp;
                        <b>🔥 Remix?:</b> {row['Remix?']}<br>
                        <b>🎚️ Level:</b> {row['Dance Level']} &nbsp;&nbsp;
                        <b>🎧 Mood:</b> {row['Mood']} &nbsp;&nbsp;
                        <b>🎛️ Tempo:</b> {row['Tempo']}<br>
                        <b>👤 Submitted By:</b> {row['Submitted By']} &nbsp;&nbsp;
                        <b>📌 Status:</b> {row['Status']} &nbsp;&nbsp;
                        <b>🎯 Request:</b> {row['Request Type']}<br>
                        <b>🎵 Need Music?</b> {row['Need Music']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

# --- FOOTER ---
st.markdown("---")
st.caption("🎛 Powered by VibeQue • DJ Admin View Only • #LETSWORK")
