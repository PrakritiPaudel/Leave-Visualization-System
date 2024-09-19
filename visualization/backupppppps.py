import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import warnings
from datetime import date
from services.employee import load_employee_details
from services.fiscal import load_fiscal_years
from services.leave import load_data, load_leave_types
from services.upload import upload_file

warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='visualization/.env.streamlit')

# Set up Streamlit page configuration
st.set_page_config(page_title="Leave Visualization Dashboard", page_icon="🌴", layout="wide")

# Custom CSS to improve the look and feel
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stApp { background-color: #f0f2f6; }
    .chart-container {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .status-approved { color: green; }
    .status-rejected { color: red; }
    </style>
""", unsafe_allow_html=True)

st.title("🌴 Leave Visualization Dashboard")

# Sidebar for controls
with st.sidebar:
    st.header("Filter Options")
    
    fiscal_years_df = load_fiscal_years()
    fiscal_year_dict = dict(zip(fiscal_years_df['fiscal_year'], fiscal_years_df['fiscal_start_date'].astype(str) + ' - ' + fiscal_years_df['fiscal_end_date'].astype(str)))

    selected_fiscal_year = st.selectbox("Select Fiscal Year", options=list(fiscal_year_dict.keys()))

    if selected_fiscal_year:
        fiscal_year_dates = fiscal_years_df[fiscal_years_df['fiscal_year'] == selected_fiscal_year].iloc[0]
        start_date = pd.to_datetime(fiscal_year_dates['fiscal_start_date'])
        end_date = pd.to_datetime(fiscal_year_dates['fiscal_end_date'])
    else:
        start_date = pd.to_datetime("2023-01-01")
        end_date = pd.to_datetime("2023-12-31")

    start_date = st.date_input("Start Date", start_date)
    end_date = st.date_input("End Date", end_date)

    leave_types_df = load_leave_types()
    leave_type_dict = dict(zip(leave_types_df['id'], leave_types_df['leave_type']))

    selected_leave_type_id = st.selectbox(
        "Select Leave Type",
        options=list(leave_type_dict.keys()),
        format_func=lambda x: leave_type_dict[x]
    )

    st.header("Data Upload")
    if st.button("Upload New File"):
        st.session_state.show_file_upload = True
    else:
        st.session_state.show_file_upload = False

# Create tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Employee Analysis", "Today's Leaves"])

if st.session_state.get('show_file_upload', False):
    with tab1:
        st.header("Load new file from device or drag it here")
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"], on_change=upload_file, key='file')
else:
    df = load_data(start_date, end_date)

    with tab1:
        st.header("Leave Overview")
        
        # Summary statistics
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        if not df.empty:
            col1.metric("Total Leave Days", f"{df['leave_days'].sum():.0f}")
            col2.metric("Average Leave Duration", f"{df['leave_days'].mean():.1f} days")
            col3.metric("Total Employees on Leave", df['employee_id'].nunique())
            most_common_leave_type = leave_type_dict.get(df['leave_type_id'].mode().iloc[0], "N/A")
            col4.metric("Most Common Leave Type", most_common_leave_type)
        else:
            col1.metric("Total Leave Days", "No data")
            col2.metric("Average Leave Duration", "No data")
            col3.metric("Total Employees on Leave", "No data")
            col4.metric("Most Common Leave Type", "No data")

        # Visualizations
        if not df.empty:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            leave_status_chart = px.bar(
                df.groupby('leave_status').agg({'leave_days': 'sum'}).reset_index(),
                x='leave_status',
                y='leave_days',
                title='Total Leave Days by Status',
                color='leave_status',
                color_discrete_map={'Approved': 'green', 'Rejected': 'red', 'Pending': 'yellow'},
                height=400
            )
            leave_status_chart.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(leave_status_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            leave_type_distribution = px.pie(
                df,
                names='leave_type_id',
                title='Leave Type Distribution',
                height=400,
                labels=leave_type_dict
            )
            leave_type_distribution.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(leave_type_distribution, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            leave_days_over_time = px.line(
                df.groupby('start_date').agg({'leave_days': 'sum'}).reset_index(),
                x='start_date',
                y='leave_days',
                title='Leave Trends Over Time',
                height=400
            )
            leave_days_over_time.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(leave_days_over_time, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Handling the missing 'department' column
            if 'department' in df.columns:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                dept_leave_dist = px.bar(
                    df.groupby('department').agg({'leave_days': 'sum'}).reset_index(),
                    x='department',
                    y='leave_days',
                    title='Leave Distribution by Department',
                    color='department',
                    height=400
                )
                dept_leave_dist.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(dept_leave_dist, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Department information is not available in the current dataset.")

            # New chart: Monthly Leave Patterns
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            df['month'] = pd.to_datetime(df['start_date']).dt.strftime('%B')
            monthly_patterns = px.box(
                df,
                x='month',
                y='leave_days',
                title='Monthly Leave Patterns',
                height=400
            )
            monthly_patterns.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(monthly_patterns, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.warning("No data available for the selected period.")

    with tab2:
        st.header("Employee Leave Analysis")
        
        # Load employee data
        df = load_data(start_date, end_date)

        if df is None or df.empty:
            st.warning("No leave data available. Please check your data source or filters.")
        else:
            # Check available columns
            st.write("Available columns:", df.columns.tolist())
            
            # Try to identify employee ID and name columns
            emp_id_col = next((col for col in df.columns if 'id' in col.lower()), None)
            emp_name_col = next((col for col in df.columns if 'name' in col.lower()), None)
            
            if emp_id_col is None or emp_name_col is None:
                st.error(f"Unable to identify employee ID and name columns. Please ensure your data includes these columns.")
                st.stop()

            # Get unique employee names and IDs
            employee_data = df[[emp_id_col, emp_name_col]].drop_duplicates()
            employee_names = employee_data[emp_name_col].tolist()
            
            # Create a dictionary to map employee names to IDs
            employee_name_to_id = dict(zip(employee_data[emp_name_col], employee_data[emp_id_col]))

            # Add CSS for improved selectbox appearance
            st.markdown("""
                <style>
                .employee-select-container {
                    margin-top: -15px;
                }
                .employee-select-label {
                    font-size: 16px !important;
                    font-weight: bold !important;
                    margin-bottom: 2px !important;
                    display: inline-block;
                }
                .employee-select {
                    font-size: 14px !important;
                    padding: 2px 5px !important;
                    border: 1px solid #ccc !important;
                    border-radius: 4px !important;
                    width: auto !important;
                    display: inline-block !important;
                }
                .stSelectbox > div > div {
                    min-height: 20px !important;
                }
                </style>
                """, unsafe_allow_html=True)

            # Use HTML to create the compact layout
            st.markdown('<div class="employee-select-container">', unsafe_allow_html=True)
            st.markdown('<span class="employee-select-label">Select an Employee:</span>', unsafe_allow_html=True)
            selected_employee_name = st.selectbox("", options=employee_names, key="employee_select", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            if selected_employee_name:
                selected_employee_id = employee_name_to_id[selected_employee_name]
                employee_df = df[df[emp_id_col] == selected_employee_id]

                if employee_df.empty:
                    st.info(f"No leave data available for {selected_employee_name}.")
                else:
                    st.subheader(f"Leave Data for {selected_employee_name}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        if 'leave_type' in employee_df.columns:
                            employee_leave_type = px.pie(
                                employee_df,
                                names='leave_type',
                                title='Leave Type Distribution',
                                height=300,
                                labels={'leave_type': 'Leave Type'}
                            )
                            employee_leave_type.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                            st.plotly_chart(employee_leave_type, use_container_width=True)
                        else:
                            st.warning("Leave type information is not available in the dataset.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        if 'leave_status' in employee_df.columns and 'leave_days' in employee_df.columns:
                            employee_leave_status = px.bar(
                                employee_df.groupby('leave_status').agg({'leave_days': 'sum'}).reset_index(),
                                x='leave_status',
                                y='leave_days',
                                title='Leave Days by Status',
                                color='leave_status',
                                color_discrete_map={'Approved': 'green', 'Rejected': 'red', 'Pending': 'yellow'},
                                height=300
                            )
                            employee_leave_status.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                            st.plotly_chart(employee_leave_status, use_container_width=True)
                        else:
                            st.warning("Leave status or days information is not available in the dataset.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    if 'start_date' in employee_df.columns and 'leave_days' in employee_df.columns and 'leave_type' in employee_df.columns:
                        employee_leave_timeline = px.scatter(
                            employee_df,
                            x='start_date',
                            y='leave_days',
                            size='leave_days',
                            color='leave_type',
                            hover_data=['leave_status'] if 'leave_status' in employee_df.columns else None,
                            title='Leave History Timeline',
                            height=400,
                            labels={'leave_type': 'Leave Type'}
                        )
                        employee_leave_timeline.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(employee_leave_timeline, use_container_width=True)
                    else:
                        st.warning("Required information for timeline chart is not available in the dataset.")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.subheader("Detailed Leave Records")
                    display_columns = [col for col in ['start_date', 'end_date', 'leave_type', 'leave_status', 'leave_days'] if col in employee_df.columns]
                    if display_columns:
                        styled_df = employee_df[display_columns].style.applymap(
                            lambda x: 'color: green' if x == 'Approved' else ('color: red' if x == 'Rejected' else ''),
                            subset=['leave_status'] if 'leave_status' in display_columns else []
                        )
                        st.dataframe(styled_df)
                    else:
                        st.warning("No detailed leave records available to display.")
            else:
                st.info("Please select an employee to view their leave analysis.")

    with tab3:
        st.header("Today's Leaves")
        today = date.today()
        # Convert start_date and end_date to datetime
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce').dt.date
        df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.date

        # Filter for today's leaves
        today = date.today()
        today_leaves = df[(df['start_date'] <= today) & (df['end_date'] >= today)]
        
        if not today_leaves.empty:
            st.subheader(f"Employees on Leave Today ({today})")
            
            for _, row in today_leaves.iterrows():
                employee_id = row['employee_id']
                leave_type = leave_type_dict[row['leave_type_id']]
                leave_status = row['leave_status']
                total_days = row['leave_days']
                
                status_color = 'status-approved' if leave_status == 'Approved' else 'status-rejected' if leave_status == 'Rejected' else ''
                
                st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                        <h4>Employee ID: {employee_id}</h4>
                        <p>Leave Type: {leave_type}</p>
                        <p>Status: <span class="{status_color}">{leave_status}</span></p>
                        <p>Total Days: {total_days}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No employees are on leave today.")

        # Summary of leaves by status
        st.subheader("Today's Leave Summary")
        status_counts = today_leaves['leave_status'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values, hole=.3)])
        fig.update_layout(title_text="Leave Status Distribution")
        st.plotly_chart(fig) 