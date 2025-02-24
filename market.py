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
from PIL import Image




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

def send_confirmation_email(name, email, date, party_size, event_time):
    """Send confirmation email using Gmail SMTP"""
    sender_email = "passageincambridge@gmail.com"
    
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



# Configure Streamlit Page
st.set_page_config(
    page_title="🍷 The Taste & Toast Experience",
    page_icon="🥂",
    layout="centered"
)

# logo = Image.open("passagetoindia2.png")  # Ensure "logo.png" is in your working directory
# st.image(logo)
st.markdown("<div style='text-align: center;'><img src='https://passageindia.com/wp-content/uploads/passagetoindia2.png' width='150'></div>", unsafe_allow_html=True)


# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

# Weekly Event Data
DAILY_EVENTS = [
    {"day": "Monday", "event": "🍹 Spice Symphony", "info": "Indian Curry & Wine Pairing Night", "more info": "A curated 3-course meal, paired with a Exquisite wine"},
    {"day": "Tuesday", "event": "🧀 Royal Feast", "info": "Nawabi Biryani & Craft Beverage Night", "more info": "Indulge in the rich, aromatic flavors of Indian Rice Dishes, paired with artisanal drinks."},
    {"day": "Wednesday", "event": "🍷 Spirits & Spices", "info": "Indian-Inspired Cocktails", "more info": "Indulge in the rich, aromatic flavors of Hyderabad & Lucknow, paired with artisanal drinks."},
    {"day": "Thursday", "event": "🍸 Bollywood Night", "info": "Chaat & Mocktail/ Cocktail Fiesta", "more info": "A lively Bollywood evening featuring street food & vibrant drinks"},
    {"day": "Friday", "event": "🔥 Healthy Tandoor & Whiskey Tales", "info": "Grill & Whiskey Appreciation Night", "more info": "grilled smoky tandoori delicacies, complemented by fine whiskey"},
    {"day": "Saturday", "event": "🥂 The Maharaja Thali", "info": "Indian Curry & infused drink Pairing Night", "more info": "A lavish 3-course meal paired with infused drinks"},
    {"day": "Sunday", "event": "👨‍🍳 Sweet Endings", "info": "Indian Dessert & Chai Pairing", "more info": "A decadent Indian dessert tasting paired with gourmet chai"}
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
        <h2>✨ Tonight's Experience✨</h2>
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
        event_time = st.time_input("Preferred time", value=start_time, step=300)

        if st.form_submit_button("Confirm Reservation"):
            if start_time <= event_time <= end_time:
                if send_confirmation_email(name, email, event_date, party_size, event_time):
                    log_event("Reservation", f"{name} booked for {event_date} at {event_time}")
                    st.success(f"✅ Reservation confirmed for {event_date} at {event_time.strftime('%I:%M %p')}!")
                else:           
                    st.error("There was an issue confirming your reservation. Please try again or contact us directly at +1 615-497-6113.")

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
            st.success(f"ℹ️ {row['more info']}")

