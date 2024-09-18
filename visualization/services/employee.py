import os
import pandas as pd
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


def load_employee_details(emp_id):
    response = requests.get(f"{api_endpoint}/employee/{emp_id}")

    # Check if the response status code is OK (200)
    if response.status_code != 200:
        st.error(f"Failed to fetch employee details: Status code {response.status_code}")
        return None

    # Try to decode the response as JSON
    try:
        data = response.json()
    except ValueError:
        st.error("Invalid JSON response from the API")
        return None
    
    # If the data is empty or invalid, handle that case
    if not data:
        st.error("No data found for this employee")
        return None
    print(data)
    return pd.DataFrame.from_dict(data)