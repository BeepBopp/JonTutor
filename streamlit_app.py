import streamlit as st

st.set_page_config(page_title="Login", page_icon="📖")

st.title("📖 Welcome to Jon Tutor")

# Initialize storage for users in session_state
if 'users' not in st.session_state:
    st.session_state.users = {}  # Empty dict to store username: password

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# Function to handle login
def login(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success(f"✅ Logged in as {username}")
    else:
        st.error("❌ Incorrect username or password.")

# Function to handle account creation
def create_account(new_user, new_pass, confirm_pass):
    if new_user == "" or new_pass == "":
        st.warning("Please enter a valid username and password.")
    elif new_user in st.session_state.users:
        st.warning("That username is already taken.")
    elif new_pass != confirm_pass:
        st.warning("Passwords do not match.")
    else:
        st.session_state.users[new_user] = new_pass
        st.success("🎉 Account created! You can now log in.")

# Show content based on login state
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Login"):
                login(username, password)

        with col2:
            if st.button("Forgot Password?"):
                st.info('📧 Please contact **rxu187@gmail.com** to reset your password.')

    with tab2:
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")

        if st.button("Create Account"):
            create_account(new_user, new_pass, confirm_pass)

else:
    st.success(f"✅ You are logged in as `{st.session_state.username}`.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
