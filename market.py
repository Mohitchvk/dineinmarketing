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

def upload_to_s3(data, bucket_name, key):
    """Upload data to S3"""
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
    """Log user visits to S3"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'user_id': st.session_state.get("user_id", "unknown"),
        'page': 'main'
    }
    key = f"logs/{st.session_state.get('user_id', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    upload_to_s3(log_data, "passage-marketing", key)

# Configure Streamlit Page
st.set_page_config(
    page_title="🍷 The Taste & Toast Experience",
    page_icon="🥂",
    layout="centered"
)

# Initialize session state for user tracking
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

# Daily Promotions (Massachusetts-compliant)
DAILY_OFFERS = {
    0: "Monday Masterclass: Craft Cocktail Education Session",
    1: "Tuesday Tasting: Artisanal Cheese Pairing Experience", 
    2: "Wine Wednesday: Regional Varietal Exploration",
    3: "Throwback Thursday: Historical Mixology Demo",
    4: "Firepit Friday: Live Patio Music & Mixology",
    5: "Saturday Cellar: Rare Reserve Tasting", 
    6: "Sunday Social: Chef's Tasting Menu Preview"
}

def send_confirmation_email(name, email, date, party_size, event_time):
    """Send confirmation email using Gmail SMTP"""
    sender_email = "cu.18bcs1106@gmail.com"
    
    # Check if email password is available
    if "email" not in st.secrets or "password" not in st.secrets["email"]:
        print("Email secrets not found.")
        return False
    
    sender_password = st.secrets["email"]["password"]

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = "Reservation Confirmed at Passage"

    body = f"""
    Dear {name},

    Your reservation for {party_size} people on {date.strftime('%B %d, %Y')} at {event_time.strftime('%I:%M %p')} has been confirmed.
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

def main():
    """Main Streamlit App"""
    log_visit()
    today = datetime.today().weekday()
    
    st.title(f"Tonight's Experience: {DAILY_OFFERS[today]}")
    
    with st.expander("📅 Weekly Schedule", expanded=True):
        st.table(pd.DataFrame({
            "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "Experience": list(DAILY_OFFERS.values())
        }))
    
    st.markdown("""
    **Your Exclusive Benefits:**
    - Complimentary tasting notes with any entrée
    - Priority seating reservations
    - Educational mixology materials
    - Chef-curated pairing suggestions
    """)

# Allowed reservation times
start_time = time(11, 30)  # 11:30 AM
end_time = time(22, 0)    # 10:00 PM

# Reservation Form
with st.form("reservation"):
    st.write("Reserve Your Experience")
    
    name = st.text_input("Name for reservation", key="name")
    email = st.text_input("Email address", key="email")
    party_size = st.number_input("Party size", 1, 10, key="party_size")
    event_date = st.date_input("Preferred date", key="event_date")
    
    event_time = st.time_input("Preferred time", value=start_time, step=300, key="event_time")
    
    if st.form_submit_button("Request Reservation"):
        if start_time <= event_time <= end_time:
            if send_confirmation_email(name, email, event_date, party_size, event_time):
                st.success(f"Reservation confirmed for {event_date.strftime('%B %d, %Y')} at {event_time.strftime('%I:%M %p')}! Check your email for details.")
            else:
                st.error("There was an issue confirming your reservation. Please try again or contact us directly at +1 615-497-6113.")
        else:
            st.error(f"Please select a time between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}.")

if __name__ == "__main__":
    main()
