import streamlit as st
from datetime import datetime
import pandas as pd
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from datetime import time


import boto3
import json
from botocore.exceptions import ClientError

def upload_to_s3(data, bucket_name, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["aws"]["access_key_id"],
        aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
        region_name=st.secrets["aws"]["region"]
    )
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(data)
        )
    except ClientError as error:
        # Log the error details for further inspection
        error_code = error.response['Error']['Code']
        error_message = error.response['Error']['Message']
        print(f"ClientError: {error_code} - {error_message}")
        # Optionally, re-raise the error or handle it accordingly
        raise error

# Example usage in a function
def log_visit():
    from datetime import datetime
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'user_id': st.session_state.get("user_id", "unknown"),
        'page': 'main'
    }
    # Define the S3 key for this log entry.
    key = f"logs/{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    upload_to_s3(log_data, "passage-marketing", key)

# Configure page
st.set_page_config(
    page_title="🍷 The Taste & Toast Experience",
    page_icon="🥂",
    layout="centered"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

# Massachusetts-compliant daily promotions
DAILY_OFFERS = {
    0: "Monday Masterclass: Craft Cocktail Education Session",
    1: "Tuesday Tasting: Artisanal Cheese Pairing Experience", 
    2: "Wine Wednesday: Regional Varietal Exploration",
    3: "Throwback Thursday: Historical Mixology Demo",
    4: "Firepit Friday: Live Patio Music & Mixology",
    5: "Saturday Cellar: Rare Reserve Tasting", 
    6: "Sunday Social: Chef's Tasting Menu Preview"
}

# def log_visit():
#     """Log visit data"""
#     log_data = {
#         'timestamp': datetime.now().isoformat(),
#         'user_id': st.session_state.user_id,
#         'page': 'main'
#     }
    
#     # In a production environment, you'd want to use a proper logging service
#     # For Streamlit deployment, we'll use a simple print statement
#     print(f"Visit logged: {log_data}")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_confirmation_email(name, email, date, party_size):
    """Send confirmation email using Gmail SMTP with an app password"""
    # Email configuration
    sender_email = "cu.18bcs1106@gmail.com"
    sender_password = st.secrets["email"]["password"]  # Use your generated app password here

    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = "Reservation Confirmed at Passage"

    body = f"""
    Dear {name},

    Your reservation for {party_size} on {date} has been confirmed.
    We look forward to seeing you!

    Best regards,
    The Taste & Toast Team
    """
    message.attach(MIMEText(body, 'plain'))

    # Send email
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
    # Log visit
    log_visit()
    
    today = datetime.datetime.today().weekday()
    
    st.title(f"Tonight's Experience: {DAILY_OFFERS[today]}")
    
    with st.expander("📅 Weekly Schedule", expanded=True):
        st.table(pd.DataFrame({
            "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "Experience": list(DAILY_OFFERS.values())
        }))
    
    # Value proposition
    st.markdown("""
    **Your Exclusive Benefits:**
    - Complimentary tasting notes with any entrée
    - Priority seating reservations
    - Educational mixology materials
    - Chef-curated pairing suggestions
    """)
    



# Define allowed time range
start_time = time(11, 30)  # 11:30 AM
end_time = time(22, 0)    # 10:00 PM

# Event reservation form
with st.form("reservation"):
    st.write("Reserve Your Experience")
    
    # Input fields
    name = st.text_input("Name for reservation")
    email = st.text_input("Email address")
    party_size = st.number_input("Party size", 1, 10)
    event_date = st.date_input("Preferred date")
    
    # Time selection with validation
    event_time = st.time_input("Preferred time", value=start_time, step=300)  # Default to 11:30 AM, step of 5 minutes
    
    # Submit button
    if st.form_submit_button("Request Reservation"):
        # Check if the selected time is within the allowed range
        if start_time <= event_time <= end_time:
            # Send confirmation email if time is valid
            if send_confirmation_email(name, email, event_date, party_size, event_time):
                st.success(f"Reservation confirmed for {event_date} at {event_time.strftime('%I:%M %p')}! Check your email for details.")
            else:
                st.error("There was an issue confirming your reservation. Please try again or contact us directly at +1 615-497-6113.")
        else:
            # Display error if time is outside the allowed range
            st.error(f"Please select a time between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}.")



if __name__ == "__main__":
    main()
