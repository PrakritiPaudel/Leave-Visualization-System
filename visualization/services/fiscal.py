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


def load_fiscal_years():
    try:
        response = requests.get(f"{api_endpoint}/fiscal-years")
        response.raise_for_status()
        data = response.json()

        fiscal_start_dates = data["fiscal_start_date"]
        fiscal_end_dates = data["fiscal_end_date"]

        fiscal_years_df = pd.DataFrame({
            'fiscal_start_date': fiscal_start_dates.values(),
            'fiscal_end_date': fiscal_end_dates.values()
        })

        fiscal_years_df['fiscal_year'] = pd.to_datetime(fiscal_years_df['fiscal_start_date']).dt.year.astype(str) + '-' + pd.to_datetime(fiscal_years_df['fiscal_end_date']).dt.year.astype(str)

        return fiscal_years_df
    except:
        return pd.DataFrame.from_dict({})