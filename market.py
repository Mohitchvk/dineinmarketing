import streamlit as st
from datetime import datetime
import pandas as pd
import uuid
import boto3
from botocore.exceptions import ClientError

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

# Set up CloudWatch logging
cloudwatch_client = boto3.client('logs')
log_group_name = 'streamlit_app_logs'

def log_event(message):
    timestamp = int(datetime.now().timestamp() * 1000)
    try:
        cloudwatch_client.put_log_events(
            logGroupName=log_group_name,
            logStreamName='app_events',
            logEvents=[
                {
                    'timestamp': timestamp,
                    'message': message
                }
            ]
        )
    except Exception as e:
        st.error(f"Error logging to CloudWatch: {e}")

# Set up SES client
ses_client = boto3.client('ses')

def send_confirmation_email(name, email, date, party_size):
    SENDER = "your_verified_email@example.com"
    SUBJECT = "Reservation Confirmed!"
    BODY_TEXT = f"""
    Dear {name},
    
    Your reservation for {party_size} on {date} has been confirmed.
    We look forward to seeing you!
    
    Best regards,
    The Taste & Toast Team
    """
    
    try:
        response = ses_client.send_email(
            Destination={'ToAddresses': [email]},
            Message={
                'Body': {'Text': {'Charset': "UTF-8", 'Data': BODY_TEXT}},
                'Subject': {'Charset': "UTF-8", 'Data': SUBJECT},
            },
            Source=SENDER
        )
    except ClientError as e:
        st.error(f"Error sending email: {e.response['Error']['Message']}")
        return False
    else:
        st.success("Email sent successfully!")
        return True

def main():
    log_event("App started")
    
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
    
    with st.form("reservation"):
        st.write("Reserve Your Experience")
        name = st.text_input("Name for reservation")
        email = st.text_input("Email address")
        party_size = st.number_input("Party size", 1, 10)
        event_date = st.date_input("Preferred date")
        
        if st.form_submit_button("Request Reservation"):
            log_event(f"Reservation attempt: {name}, {email}, {party_size}, {event_date}")
            if send_confirmation_email(name, email, event_date, party_size):
                st.success("Reservation confirmed! Check your email for details.")
                log_event(f"Reservation confirmed: {name}, {email}, {party_size}, {event_date}")
            else:
                st.error("There was an issue confirming your reservation. Please try again or contact us directly.")

if __name__ == "__main__":
    main()
