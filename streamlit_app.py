import streamlit as st

st.set_page_config(page_title="Jon Tutor", page_icon="📖")

pages = [
    st.page_link("assignment.py", label="Assignment", icon="✍️"),
    st.page_link("calendar.py", label="Calendar", icon="📆"),
    st.page_link("writing_tips.py", label="Writing Tips", icon="💡"),
]

nav = st.navigation(pages)
nav.run()
