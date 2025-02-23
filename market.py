import streamlit as st
import pandas as pd
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, time
import boto3
import json
from botocore.exceptions import ClientError

# Function to upload logs to S3
def upload_to_s3(data, bucket_name, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["aws"]["access_key_id"],
        aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
        region_name=st.secrets["aws"]["region"]
    )
    try:
        s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data))
    except ClientError as error:
        print(f"ClientError: {error.response['Error']['Code']} - {error.response['Error']['Message']}")
        raise error

def log_event(action, detail):
    """Logs user interactions to S3."""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'user_id': st.session_state.get("user_id", "unknown"),
        'action': action,
        'detail': detail
    }
    key = f"logs/{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    upload_to_s3(log_data, "passage-marketing", key)

# Configure Streamlit Page
st.set_page_config(
    page_title="🍷 The Taste & Toast Experience",
    page_icon="🥂",
    layout="centered"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

# Weekly Event Data
DAILY_EVENTS = [
    {"day": "Monday", "event": "🍹 Masterclass", "info": "Craft Cocktail Education Session"},
    {"day": "Tuesday", "event": "🧀 Tasting", "info": "Artisanal Cheese Pairing Experience"},
    {"day": "Wednesday", "event": "🍷 Wine Night", "info": "Regional Varietal Exploration"},
    {"day": "Thursday", "event": "🍸 Throwback", "info": "Historical Mixology Demo"},
    {"day": "Friday", "event": "🔥 Firepit", "info": "Live Patio Music & Mixology"},
    {"day": "Saturday", "event": "🥂 Cellar Reserve", "info": "Rare Reserve Tasting"},
    {"day": "Sunday", "event": "👨‍🍳 Chef’s Special", "info": "Exclusive Chef’s Tasting Menu"}
]

# Get today's experience
today = datetime.today().weekday()
tonights_experience = DAILY_EVENTS[today]

# Adaptive CSS for Light & Dark Mode
st.markdown("""
    <style>
    :root {
        --bg-color: #ffffff;
        --text-color: #333333;
        --card-bg: #f8f9fa;
        --btn-bg: #007BFF;
        --btn-text: #ffffff;
        --table-border: #dddddd;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #1e1e1e;
            --text-color: #f1f1f1;
            --card-bg: #2b2b2b;
            --btn-bg: #008CBA;
            --btn-text: #ffffff;
            --table-border: #444;
        }
    }
    .experience-card {
        background-color: var(--card-bg);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        font-size: 20px;
        color: var(--text-color);
    }
    .book-btn {
        font-size: 18px;
        padding: 12px 20px;
        width: 50%;
        border-radius: 10px;
        font-weight: bold;
        background-color: var(--btn-bg);
        color: var(--btn-text);
        display: block;
        margin: 20px auto;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid var(--table-border);
        padding: 12px;
        text-align: center;
        color: var(--text-color);
    }
    </style>
""", unsafe_allow_html=True)

# Display Tonight’s Experience
st.markdown(f"""
    <div class="experience-card">
        <h2>✨ Tonight's Experience ✨</h2>
        <p><strong>{tonights_experience["event"]}</strong> - {tonights_experience["info"]}</p>
    </div>
""", unsafe_allow_html=True)

# Centered Book Reservation Button
if st.button("📅 Book Reservation", help="Click to book your spot!", key="book_btn"):
    st.session_state.show_reservation = True

# Show reservation form only if button is clicked
if st.session_state.get("show_reservation", False):
    st.subheader("Reserve Your Experience")
    
    with st.form("reservation"):
        name = st.text_input("Name for reservation")
        email = st.text_input("Email address")
        party_size = st.number_input("Party size", 1, 100)
        event_date = st.date_input("Preferred date")
        
        start_time = time(11, 30)
        end_time = time(22, 0)
        event_time = st.time_input("Preferred time", value=start_time, step=1000)

        if st.form_submit_button("Confirm Reservation"):
            if start_time <= event_time <= end_time:
                log_event("Reservation", f"{name} booked for {event_date} at {event_time}")
                st.success(f"✅ Reservation confirmed for {event_date} at {event_time.strftime('%I:%M %p')}!")
            else:
                st.error(f"⏰ Please select a time between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}.")

# Fancy Weekly Events Table
st.markdown("### 📆 Weekly Experiences")

df = pd.DataFrame(DAILY_EVENTS)
df["More Info"] = df["info"]

# Display table with "More Info" button for each event
for index, row in df.iterrows():
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        st.markdown(f"**{row['day']}**")
    
    with col2:
        st.markdown(f"{row['event']} - {row['info']}")
    
    with col3:
        if st.button(f"ℹ️ More Info", key=f"info_{index}"):
            log_event("More Info Clicked", f"User checked details for {row['event']}")
            st.success(f"ℹ️ {row['info']}")

