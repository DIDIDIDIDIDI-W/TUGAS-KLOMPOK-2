
import streamlit as st
import http.server
import socketserver
import threading
import os

# --- Configuration ---
PORT = 8000
DIRECTORY = "."  # Serve files from the root directory

# --- Set up Streamlit page ---
st.set_page_config(
    page_title="Excel Regression Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Helper to serve files in a background thread ---
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    """Starts a simple HTTP server in a background thread."""
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# Check if the server is already running (to avoid restarting on every Streamlit rerun)
if 'server_thread' not in st.session_state:
    # Start the server in a new thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    st.session_state.server_thread = server_thread
    print("Started background server thread.")

# --- Main App Display ---

# Hide Streamlit's default header and footer for a more integrated look
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Use an iframe to embed the React application
# The URL points to the index.html file served by our background server.
st.components.v1.iframe(f"http://localhost:{PORT}/index.html", height=1000, scrolling=True)

