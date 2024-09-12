import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
import warnings

warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='/myapp/visualization/.env.streamlit')

# Set up Streamlit page configuration
st.set_page_config(page_title="Leave Visualization System", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Leave Visualization System")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# Get the API endpoint
api_endpoint = os.getenv('API_ENDPOINT')

if api_endpoint is None:
    st.error("API_ENDPOINT environment variable is not set")
    raise ValueError("API_ENDPOINT environment variable is not set")

def upload_file():
    file = st.session_state['file']
    if(file == None):
        return
    files = {"file": (file.name, file.getvalue(), file.type)}
    response = requests.post(os.getenv('API_ENDPOINT')+'/upload',files= files)
    return response

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"], on_change=upload_file, key='file')
# upload_file(uploaded_file)
# Load environment variables from .env file


def load_data(start_date, end_date):
    response = requests.get(os.getenv('API_ENDPOINT')+'/leaves'+'?start_date='+start_date.isoformat()+'&end_date='+end_date.isoformat())
    data= response.json()
    return pd.DataFrame.from_dict(data)
    
# # Date Range Selector
# start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
# end_date = st.date_input("End Date", pd.to_datetime("2023-12-31"))

def load_leave_types():
    response = requests.get(os.getenv('API_ENDPOINT')+'/leave-types')
    data= response.json()
    return pd.DataFrame.from_dict(data)
# neww
def load_fiscal_years():
    response = requests.get(os.getenv('API_ENDPOINT') + '/fiscal-years')
    data = response.json()

    # Flatten the data
    fiscal_start_dates = data["fiscal_start_date"]
    fiscal_end_dates = data["fiscal_end_date"]

    # Convert to DataFrame
    fiscal_years_df = pd.DataFrame({
        'fiscal_start_date': fiscal_start_dates.values(),
        'fiscal_end_date': fiscal_end_dates.values()
    })

     # Add a new column for fiscal year in the format "2021-2022"
    fiscal_years_df['fiscal_year'] = pd.to_datetime(fiscal_years_df['fiscal_start_date']).dt.year.astype(str) + '-' + pd.to_datetime(fiscal_years_df['fiscal_end_date']).dt.year.astype(str)

    return fiscal_years_df

# Load fiscal years
fiscal_years_df = load_fiscal_years()

# Create a dictionary for fiscal year selection
fiscal_year_dict = dict(zip(fiscal_years_df['fiscal_year'], fiscal_years_df['fiscal_start_date'].astype(str) + ' - ' + fiscal_years_df['fiscal_end_date'].astype(str)))

# Dropdown for selecting fiscal year
selected_fiscal_year = st.selectbox(
    "Select Fiscal Year",
    options=list(fiscal_year_dict.keys())
)

# Get selected fiscal year dates
if selected_fiscal_year:
    fiscal_year_dates = fiscal_years_df[fiscal_years_df['fiscal_year'] == selected_fiscal_year].iloc[0]
    start_date = pd.to_datetime(fiscal_year_dates['fiscal_start_date'])
    end_date = pd.to_datetime(fiscal_year_dates['fiscal_end_date'])
else:
    start_date = pd.to_datetime("2023-01-01")
    end_date = pd.to_datetime("2023-12-31")

print(3, selected_fiscal_year)

# Date Range Selector (updated based on selected fiscal year)
start_date = st.date_input("Start Date", start_date)
end_date = st.date_input("End Date", end_date)

# Load data
df = load_data(start_date, end_date)

# Display the data as a table
st.write("### Leave Data", df)

# Bar chart: Total leave days by leave status
if not df.empty:
    leave_status_chart = px.bar(
        df.groupby('leave_status').agg({'leave_days': 'sum'}).reset_index(),
        x='leave_status',
        y='leave_days',
        title='Total Leave Days by Leave Status'
    )
    st.plotly_chart(leave_status_chart)

    # Line chart: Leave days over time
    leave_days_over_time = px.line(
        df.groupby('start_date').agg({'leave_days': 'sum'}).reset_index(),
        x='start_date',
        y='leave_days',
        title='Leave Days Over Time'
    )
    st.plotly_chart(leave_days_over_time)

    # Histogram: Distribution of leave days
    leave_days_histogram = px.histogram(
        df,
        x='leave_days',
        nbins=20,
        title='Distribution of Leave Days'
    )
    st.plotly_chart(leave_days_histogram)

    # Pie chart: Leave types distribution
    leave_type_distribution = px.pie(
        df,
        names='leave_type_id',
        title='Leave Type Distribution'
    )
    st.plotly_chart(leave_type_distribution)

# Load leave types
leave_types_df = load_leave_types()

# Create a dictionary for leave type selection
leave_type_dict = dict(zip(leave_types_df['id'], leave_types_df['leave_type']))

# Dropdown for selecting leave type
selected_leave_type_id = st.selectbox(
    "Select Leave Type",
    options=list(leave_type_dict.keys()),
    format_func=lambda x: leave_type_dict[x]
)

# Load filtered data
# filtered_df = load_data(filtered_query)

filtered_df = df[df["leave_type_id"]== selected_leave_type_id] 
st.write("### Filtered Leave Data", filtered_df)

# Additional visualizations or data processing based on filtered data can be added here