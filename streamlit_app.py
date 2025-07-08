
import streamlit as st

# Set page config
st.set_page_config(page_title="Jon Tutor", page_icon="🛡📖")

# Define pages using file paths
assignment = st.Page("assignment.py", title="Assignment", icon="✍️")
calendar = st.Page("calendar.py", title="Calendar", icon="📆")
writing_tips = st.Page("writing_tips.py", title="Writing Tips", icon="💡")

# Create navigation
pg = st.navigation([assignment, calendar, writing_tips])

pg.run()
