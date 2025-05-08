import os
import streamlit as st
import requests
from dotenv import load_dotenv
import warnings

warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='.env.streamlit')
# Get the API endpoint
api_endpoint = os.getenv('SERVER_ENDPOINT')
if api_endpoint is None:
    st.error("API_ENDPOINT environment variable is not set")
    raise ValueError("API_ENDPOINT environment variable is not set")


def upload_file():
    file = st.session_state['file']
    
    if file is None:
        return
    
    headers = {
        'Authorization': f'Bearer {st.session_state.token}'
    }
    
    # Prepare the file for upload
    files = {"file": (file.name, file.getvalue(), file.type)}
    
    # Make the post request - the requests library will automatically set
    # the correct Content-Type header for multipart/form-data
    response = requests.post(f"{api_endpoint}/upload", files=files, headers=headers)
    
    return response