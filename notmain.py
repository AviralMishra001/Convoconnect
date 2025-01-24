import streamlit as st
import random
import string
import time
import sqlite3

# Database setup
def get_database_connection():
    """Creates a new SQLite connection for the current thread."""
    conn = sqlite3.connect("chat_app.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

def initialize_database():
    """Initializes the database with required tables."""
    conn = get_database_connection()
    c = conn.cursor()
    # Create channels table
    c.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    # Create messages table
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            channel_id TEXT,
            username TEXT,
            message TEXT,
            timestamp TEXT,
            FOREIGN KEY(channel_id) REFERENCES channels(id)
        )
    """)
    # Create active users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS active_users (
            channel_id TEXT,
            username TEXT,
            PRIMARY KEY (channel_id, username),
            FOREIGN KEY(channel_id) REFERENCES channels(id)
        )
    """)
    conn.commit()
    conn.close()

initialize_database()

# Helper functions
def generate_channel_id(length=8):
    """Generates a random channel ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_channel(channel_name):
    """Creates a new channel and returns its ID."""
    conn = get_database_connection()
    channel_id = generate_channel_id()
    with conn:
        conn.execute("INSERT INTO channels (id, name) VALUES (?, ?)", (channel_id, channel_name))
    return channel_id

def get_channel_name(channel_id):
    """Fetches the name of a channel given its ID."""
    conn = get_database_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM channels WHERE id = ?", (channel_id,))
    result = c.fetchone()
    return result["name"] if result else None

def save_message(channel_id, username, message):
    """Saves a message to the database."""
    conn = get_database_connection()
    with conn:
        conn.execute("""
            INSERT INTO messages (channel_id, username, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (channel_id, username, message, time.strftime("%Y-%m-%d %H:%M:%S")))

def get_messages(channel_id):
    """Retrieves all messages for a channel."""
    conn = get_database_connection()
    c = conn.cursor()
    c.execute("""
        SELECT username, message, timestamp FROM messages
        WHERE channel_id = ?
        ORDER BY timestamp ASC
    """, (channel_id,))
    return [{"username": row["username"], "text": row["message"], "timestamp": row["timestamp"]} for row in c.fetchall()]

def add_active_user(channel_id, username):
    """Adds a user to the active users table."""
    conn = get_database_connection()
    with conn:
        conn.execute("INSERT OR IGNORE INTO active_users (channel_id, username) VALUES (?, ?)", (channel_id, username))

def remove_active_user(channel_id, username):
    """Removes a user from the active users table."""
    conn = get_database_connection()
    with conn:
        conn.execute("DELETE FROM active_users WHERE channel_id = ? AND username = ?", (channel_id, username))

def get_active_users(channel_id):
    """Fetches all active users in a channel."""
    conn = get_database_connection()
    c = conn.cursor()
    c.execute("""
        SELECT username FROM active_users
        WHERE channel_id = ?
    """, (channel_id,))
    return [row["username"] for row in c.fetchall()]

# Streamlit app
st.title("ConvoConnect")

if "username" not in st.session_state:
    st.session_state.username = None
if "channel_id" not in st.session_state:
    st.session_state.channel_id = None

# Welcome page
if st.session_state.username is None or st.session_state.channel_id is None:
    st.markdown("## Welcome to ConvoConnect!")
    
    # Username input
    if st.session_state.username is None:
        username = st.text_input("Enter your username")
        if st.button("Save Username"):
            if username.strip():
                st.session_state.username = username
            else:
                st.error("Please enter a valid username.")

    # Create or join channel
    if st.session_state.username is not None:
        st.markdown("### Create or Join a Channel")
        if st.button("Create Channel"):
            channel_name = f"Channel-{st.session_state.username}"
            channel_id = create_channel(channel_name)
            st.session_state.channel_id = channel_id
            add_active_user(channel_id, st.session_state.username)
            st.success(f"Channel Created: {channel_name} (ID: {channel_id})")
            st.info("Share this Channel ID with others to join.")
        channel_id = st.text_input("Enter Channel ID to Join")
        if st.button("Join Channel"):
            channel_name = get_channel_name(channel_id)
            if channel_name:
                st.session_state.channel_id = channel_id
                add_active_user(channel_id, st.session_state.username)
                st.success(f"Joined Channel: {channel_name}")
            else:
                st.error("Invalid Channel ID.")
else:
    # Chat interface
    channel_name = get_channel_name(st.session_state.channel_id)
    st.sidebar.markdown(f"**Welcome, {st.session_state.username}!**")
    st.sidebar.markdown(f"**Channel: {channel_name}**")
    active_users = get_active_users(st.session_state.channel_id)
    st.sidebar.markdown("### Active Users")
    for user in active_users:
        st.sidebar.markdown(f"- {user}")

    # Chat messages
    st.markdown(f"### Chat: {channel_name}")
    messages = get_messages(st.session_state.channel_id)
    for msg in messages:
        st.markdown(f"**{msg['username']}** ({msg['timestamp']}): {msg['text']}")

    time.sleep(1)
    # Send message
    def send_message():
        message = st.session_state["message_input"].strip()
        if message:
            save_message(st.session_state.channel_id, st.session_state.username, message)
            st.session_state["message_input"] = ""

    st.text_input("Type your message and press Enter", key="message_input", on_change=send_message)
