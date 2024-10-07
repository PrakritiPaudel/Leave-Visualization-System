import os
import pandas as pd
import streamlit as st
import requests
from dotenv import load_dotenv
import warnings

warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='/myapp/visualization/.env.streamlit')
# Get the API endpoint
api_endpoint = os.getenv('API_ENDPOINT')
if api_endpoint is None:
    st.error("API_ENDPOINT environment variable is not set")
    raise ValueError("API_ENDPOINT environment variable is not set")


def load_data(start_date, end_date, leave_type_id):
    try:
        # response = requests.get(f"{api_endpoint}/leaves?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}")
        params = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'leave_type': leave_type_id
        }
        response = requests.get(f"{api_endpoint}/leaves", params=params)
        response.raise_for_status()

        data = response.json()
        return pd.DataFrame.from_dict(data)
    except:
        return pd.DataFrame.from_dict({})

def load_leave_types():
    try:
        response = requests.get(f"{api_endpoint}/leave-types")
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame.from_dict(data)
    except:
        return pd.DataFrame.from_dict({})