import streamlit as st

st.markdown(
    """
    <style>
    body {
        background-color: #d5d5d6;
        color: white;
    }
    [data-testid="stSidebar"] {
        background-color: #87CEEB;
        color: black;
    }
    [data-testid="stSidebar"] h2 {
        color: #2f3136;  
        font-weight: bold;
    }
    .stRadio > label {
        color: black; 
        font-size: 30px;
    }
    .stRadio > div > label {
        color: white !important; 
    }
    input[type="text"] {
        color: black;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        width: 90%;
    }
    .main-content {
        background-color: #36393F;
        color: white;
        padding: 20px;
        border-radius: 10px;
        max-width: 1200px;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Step 1: Initialize Session State
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Step 2: Welcome Page to Get the User's Name
if st.session_state.username is None:
    st.markdown(
        """
        <div class="welcome-container" style="text-align: center; margin-top: 50px;">
            <h1>Welcome to ConvoConnect!</h1>
            <p>Enter your username to join the chat.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input field for username
    username = st.text_input("Enter your username", key="username_input", label_visibility="collapsed")
    
    # Button to confirm username
    if st.button("Join Chat"):
        if username.strip():
            st.session_state.username = username
            st.rerun()  # Refresh to load the main interface
        else:
            st.error("Please enter a valid username.")
else:
    # Step 3: Main Chat Interface
    st.sidebar.markdown(f"**Welcome, {st.session_state.username}!**", unsafe_allow_html=True)
    st.sidebar.markdown("<h2>ConvoConnect</h2>", unsafe_allow_html=True)

    # Add channels dynamically
    if "channels" not in st.session_state:
        st.session_state.channels = ["General"]

    new_channel = st.sidebar.text_input("Add Channel")
    if st.sidebar.button("Enter"):
        if new_channel and new_channel not in st.session_state.channels:
            st.session_state.channels.append(new_channel)

    # Display channels
    selected_channel = st.sidebar.radio("Channels", st.session_state.channels)

    # Step 4: Display Chat History
    st.markdown(f"""
        <div class="main-content">
            <h2>Chat: #{selected_channel}</h2>
        </div>
    """, unsafe_allow_html=True)
    st.write("### Chat Area")
    for message in st.session_state.chat_history:
        st.markdown(f"**{message['username']}**: {message['text']}")

    # Step 5: Input Field for Messages
    def send_message():
        message = st.session_state["message_input"].strip()
        if message:
            # Append message to chat history
            st.session_state.chat_history.append({"username": st.session_state.username, "text": message})
            # Clear input field
            st.session_state["message_input"] = ""

    st.text_input("Type your message and press Enter", key="message_input", on_change=send_message)
