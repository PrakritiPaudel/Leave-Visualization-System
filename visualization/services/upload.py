import os
import streamlit as st
import requests
from dotenv import load_dotenv
import warnings

warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='visualization/.env.streamlit')
# Get the API endpoint
api_endpoint = os.getenv('API_ENDPOINT')
if api_endpoint is None:
    st.error("API_ENDPOINT environment variable is not set")
    raise ValueError("API_ENDPOINT environment variable is not set")


def upload_file():
    file = st.session_state['file']
    if file is None:
        return
    files = {"file": (file.name, file.getvalue(), file.type)}
    response = requests.post(f"{api_endpoint}/upload", files=files)
    return response