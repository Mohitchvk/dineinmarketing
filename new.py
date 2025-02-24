import streamlit as st
import datetime

# Define the allowed time range
start_time = datetime.time(11, 30)  # 11:30 AM
end_time = datetime.time(22, 0)    # 10:00 PM

# Add a time input widget
selected_time = st.time_input("Select a time:", value=start_time, step=300)  # Step is set to 5 minutes (300 seconds)

# Validate the selected time
if start_time <= selected_time <= end_time:
    st.success(f"You selected a valid time: {selected_time}")
else:
    st.error(f"Please select a time between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}")
