import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import warnings
from services.employee import load_employee_details
from services.fiscal import load_fiscal_years
from services.leave import load_data,load_leave_types
from services.upload import upload_file

warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='visualization/.env.streamlit')

# Set up Streamlit page configuration
st.set_page_config(page_title="Leave Visualization System", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Leave Visualization System")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"], on_change=upload_file, key='file')

# Load fiscal years
fiscal_years_df = load_fiscal_years()

# Create a dictionary for fiscal year selection
fiscal_year_dict = dict(zip(fiscal_years_df['fiscal_year'], fiscal_years_df['fiscal_start_date'].astype(str) + ' - ' + fiscal_years_df['fiscal_end_date'].astype(str)))

# Dropdown for selecting fiscal year
selected_fiscal_year = st.selectbox("Select Fiscal Year", options=list(fiscal_year_dict.keys()))

# Get selected fiscal year dates
if selected_fiscal_year:
    fiscal_year_dates = fiscal_years_df[fiscal_years_df['fiscal_year'] == selected_fiscal_year].iloc[0]
    start_date = pd.to_datetime(fiscal_year_dates['fiscal_start_date'])
    end_date = pd.to_datetime(fiscal_year_dates['fiscal_end_date'])
else:
    start_date = pd.to_datetime("2023-01-01")
    end_date = pd.to_datetime("2023-12-31")

# Date Range Selector (updated based on selected fiscal year)
start_date = st.date_input("Start Date", start_date)
end_date = st.date_input("End Date", end_date)

# Load leave data
df = load_data(start_date, end_date)

def set_employee_details_link(emp_id):
    # Set the query parameter 'emp_id' to the selected employee's ID
    st.query_params.from_dict({'emp_id':emp_id})
    return f"View Employee {emp_id}"

# Check if 'emp_id' exists in the query parameters
# Get query parameters
selected_employee_id = st.query_params.get('emp_id', None)
if selected_employee_id:
    st.write(f"## Employee Details for ID: {selected_employee_id}")

    # Fetch and display the employee's detailed information
    employee_data = load_employee_details(selected_employee_id)
    st.write(employee_data)

    # # Add back button to return to the main page
    # st.markdown(f"[Back to main page](/)")

    # Add back button to return to the main page
    if st.button("Back to main page"):
        st.switch_page("dashboard.py")
else:
    # Add employee links to the table
    if not df.empty:
        # Ensure 'employee_id' column exists
        assert 'employee_id' in df.columns, "Column 'employee_id' not found in DataFrame"
        header = st.columns([1, 1, 1])
        header[0].markdown("**employee_id**")
        header[1].markdown("**leave_status**")
        header[2].markdown("**status**")

        for index, row in df.iterrows():
            cols = st.columns([1,1,1])
            cols[0].button(row['employee_id'],on_click=set_employee_details_link,args=(row['employee_id'],),key=row['id'],)
            cols[1].write(row['leave_status'])
            cols[2].write(row['status'])

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
    filtered_df = df[df["leave_type_id"] == selected_leave_type_id]
    st.write("### Filtered Leave Data", filtered_df)

    # Additional visualizations or data processing based on filtered data can be added here
