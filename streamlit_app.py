import streamlit as st

pages = {
  st.Page("assignment.py", title="Assignment", icon="✍️"),
  st.Page("calendar.py", title="Calendar", icon="📆"),
  st.Page("writing_tips.py", title="Writing Tips", icon="💡"),
}

pg = st.navigation(pages)
st.set_page_config(page_title="Jon Tutor", page_icon="📖")
pg.run()
