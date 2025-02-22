import streamlit as st
from datetime import datetime
import pandas as pd
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


import streamlit as st
import boto3
import json

def upload_to_s3(data, bucket_name, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data)
    )

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
    upload_to_s3(log_data, "your-bucket-name", key)

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

def send_confirmation_email(name, email, date, party_size):
    """Send confirmation email"""
    # Email configuration
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    
    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = "Reservation Confirmed!"
    
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
    
    today = datetime.today().weekday()
    
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
    
    # Event reservation
    with st.form("reservation"):
        st.write("Reserve Your Experience")
        name = st.text_input("Name for reservation")
        email = st.text_input("Email address")
        party_size = st.number_input("Party size", 1, 10)
        event_date = st.date_input("Preferred date")
        
        if st.form_submit_button("Request Reservation"):
            if send_confirmation_email(name, email, event_date, party_size):
                st.success("Reservation confirmed! Check your email for details.")
            else:
                st.error("There was an issue confirming your reservation. Please try again or contact us directly.")

if __name__ == "__main__":
    main()
