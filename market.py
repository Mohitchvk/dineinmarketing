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

# Function to upload visit logs to S3
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

def log_visit():
    """Logs a user's visit to S3"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'user_id': st.session_state.get("user_id", "unknown"),
        'page': 'main'
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

# Define Weekly Experiences
DAILY_OFFERS = {
    0: "🍹 **Monday Masterclass:** Craft Cocktail Education Session",
    1: "🧀 **Tuesday Tasting:** Artisanal Cheese Pairing Experience", 
    2: "🍷 **Wine Wednesday:** Regional Varietal Exploration",
    3: "🍸 **Throwback Thursday:** Historical Mixology Demo",
    4: "🔥 **Firepit Friday:** Live Patio Music & Mixology",
    5: "🥂 **Saturday Cellar:** Rare Reserve Tasting", 
    6: "👨‍🍳 **Sunday Social:** Chef's Tasting Menu Preview"
}

# Log Visit
log_visit()

# Get today's experience
today = datetime.today().weekday()
tonights_experience = DAILY_OFFERS[today]

# Enhanced "Tonight's Experience" UI
st.markdown("""
    <style>
    .experience-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        font-size: 20px;
    }
    .book-btn {
        font-size: 18px;
        padding: 12px;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="experience-card">
        <h2>✨ Tonight's Experience ✨</h2>
        <p>{tonights_experience}</p>
    </div>
""", unsafe_allow_html=True)

# Book Reservation Button
if st.button("📅 Book Reservation", help="Click to book your spot!", key="book_btn"):
    st.session_state.show_reservation = True

# Show reservation form only if button is clicked
if st.session_state.get("show_reservation", False):
    st.subheader("Reserve Your Experience")
    
    with st.form("reservation"):
        name = st.text_input("Name for reservation")
        email = st.text_input("Email address")
        party_size = st.number_input("Party size", 1, 10)
        event_date = st.date_input("Preferred date")
        
        start_time = time(11, 30)  # 11:30 AM
        end_time = time(22, 0)    # 10:00 PM
        event_time = st.time_input("Preferred time", value=start_time, step=300)

        if st.form_submit_button("Confirm Reservation"):
            if start_time <= event_time <= end_time:
                if send_confirmation_email(name, email, event_date, party_size, event_time):
                    st.success(f"✅ Reservation confirmed for {event_date} at {event_time.strftime('%I:%M %p')}!")
                else:
                    st.error("⚠️ There was an issue confirming your reservation. Please try again.")
            else:
                st.error(f"⏰ Please select a time between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}.")

# Function to send confirmation email
def send_confirmation_email(name, email, date, party_size, event_time):
    """Send confirmation email using Gmail SMTP"""
    sender_email = "cu.18bcs1106@gmail.com"
    sender_password = st.secrets["email"]["password"]

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = "Reservation Confirmed at Passage"

    body = f"""
    Dear {name},

    Your reservation for {party_size} on {date} at {event_time.strftime('%I:%M %p')} has been confirmed.
    We look forward to seeing you!

    Best regards,
    The Taste & Toast Team
    """
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
