import streamlit as st

assignment = st.Page("assignment.py", title="Assignment", icon="✍️")
calendar = st.Page("calendar.py", title="Calendar", icon="📆")
writing_tips = st.Page("writing_tips.py", title="Writing Tips", icon="💡")

pg = st.navigation([assignment, calendar, writing_tips])
st.set_page_config(page_title="Jon Tutor", page_icon="🛡📖")
