import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dotenv import load_dotenv
import warnings
from services.fiscal import load_fiscal_years
from services.leave import load_data, load_leave_types
from services.upload import upload_file
import os
import requests


warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='.env.streamlit')

# Set up Streamlit page configuration
st.set_page_config(page_title="Leave Visualization Dashboard", page_icon="🌴", layout="wide")

# Authentication functions
def login(username, password):
    """Authenticate user and return JWT token"""
    try:
        api_endpoint = os.getenv('SERVER_ENDPOINT')
        response = requests.post(
            f"{api_endpoint}/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        return None
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None

def register(username, password):
    """Register a new user"""
    try:
        api_endpoint = os.getenv('SERVER_ENDPOINT')
        response = requests.post(
            f"{api_endpoint}/register",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            return True, "Registration successful! You can now login."
        else:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                pass
            return False, f"Registration failed: {error_detail}"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def is_authenticated():
    """Check if user is authenticated"""
    return "token" in st.session_state and st.session_state.token is not None

def logout():
    """Clear authentication data"""
    if "token" in st.session_state:
        del st.session_state.token
    if "username" in st.session_state:
        del st.session_state.username

# Custom CSS for the app with improved login/register design
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
    .status-REJECTED { color: red; }
    
    /* Enhanced Login/Register form styling */
    .auth-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 0;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        overflow: hidden;
    }
    .auth-header {
        text-align: center;
        background: linear-gradient(135deg, #34e89e 0%, #0f3443 100%);
        color: white;
        padding: 2rem 1rem;
        margin: 0 0 1.5rem 0;
        font-size: 2rem;
        font-weight: 700;
    }
    .auth-form {
        padding: 0 2rem 2rem 2rem;
    }
    .tab-container {
        display: flex;
        margin-bottom: 2rem;
    }
    .auth-tab {
        flex: 1;
        text-align: center;
        padding: 1rem;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .auth-tab.active {
        border-bottom-color: #34e89e;
        color: #0f3443;
    }
    .auth-tab:hover:not(.active) {
        background-color: #f5f5f5;
    }
    .auth-input {
        margin-bottom: 1.5rem;
    }
    .auth-input label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #333;
    }
    .auth-input input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 1rem;
    }
    .auth-button {
        width: 100%;
        padding: 0.75rem;
        background: linear-gradient(135deg, #34e89e 0%, #0f3443 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .auth-button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
    .stButton>button {
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .login-tab-btn {
        border-radius: 0 !important;
        border-bottom: 3px solid transparent !important;
        background-color: transparent !important;
        color: #333 !important;
    }
    .login-tab-btn.active {
        border-bottom-color: #34e89e !important;
        color: #0f3443 !important;
    }
    .register-tab-btn {
        border-radius: 0 !important;
        border-bottom: 3px solid transparent !important;
        background-color: transparent !important;
        color: #333 !important;
    }
    .register-tab-btn.active {
        border-bottom-color: #34e89e !important;
        color: #0f3443 !important;
    }
    /* Override Streamlit defaults */
    .stTextInput>div>div>input {
        border-radius: 6px !important;
        border: 1px solid #ddd !important;
        padding: 0.75rem !important;
    }
    .stTextInput>label {
        font-weight: 500 !important;
        color: #333 !important;
    }
    
    /* Error and success message styling */
    .stAlert {
        border-radius: 6px !important;
        margin-top: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Apply custom styles
st.markdown("""
    <style>
        .logout-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .username {
            font-size: 18px;
            font-weight: bold;
            color: #4CAF50;
        }
        .logout-button {
            background-color: #FF4C4C;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .logout-button:hover {
            background-color: #FF2A2A;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize auth_mode in session state if not present
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# Check if user is authenticated, if not show login/register form
if not is_authenticated():
    # Center the content
    _, col, _ = st.columns([1, 10, 1])
    
    with col:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Stylish header with gradient background
        st.markdown('<h1 class="auth-header">🌴 Leave Dashboard </h1>', unsafe_allow_html=True)
        
        # Custom tab navigation
        st.markdown(
            f"""
            <script>
                document.getElementById('login-tab').addEventListener('click', function() {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: 'login'
                    }}, '*');
                }});
                
                document.getElementById('register-tab').addEventListener('click', function() {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: 'register'
                    }}, '*');
                }});
            </script>
            """,
            unsafe_allow_html=True
        )
        
        # Tab buttons using Streamlit (needed for functionality since the JavaScript above doesn't work in Streamlit)
        col1, col2 = st.columns(2)
        with col1:
            login_active = "active" if st.session_state.auth_mode == "login" else ""
            if st.button("Sign In", key="login_tab", use_container_width=True, 
                       help="Switch to login form"):
                st.session_state.auth_mode = "login"
                st.rerun()
        
        with col2:
            register_active = "active" if st.session_state.auth_mode == "register" else ""
            if st.button("Create Account", key="register_tab", use_container_width=True,
                       help="Switch to registration form"):
                st.session_state.auth_mode = "register"
                st.rerun()
        
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        
        # Display appropriate form based on mode
        if st.session_state.auth_mode == "login":
            with st.form("login_form"):
                st.markdown("<h2 style='font-size: 1.5rem; margin-bottom: 1.5rem;'>Login</h2>", unsafe_allow_html=True)
                
                username = st.text_input("Username", key="login_username", 
                                       placeholder="Enter your username")
                
                password = st.text_input("Password", type="password", key="login_password", 
                                       placeholder="Enter your password")
                
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if username and password:
                        with st.spinner("Authenticating..."):
                            token = login(username, password)
                            if token:
                                st.session_state.token = token
                                st.session_state.username = username
                                st.rerun()
                            else:
                                st.error("Invalid credentials. Please try again.")
                    else:
                        st.warning("Please enter both username and password.")
        else:  # Register mode
            with st.form("register_form"):
                st.markdown("<h2 style='font-size: 1.5rem; margin-bottom: 1.5rem;'>Create Your Account</h2>", unsafe_allow_html=True)
                
                new_username = st.text_input("Choose Username", key="register_username", 
                                           placeholder="Enter a username")
                
                new_password = st.text_input("Create Password", type="password", key="register_password", 
                                           placeholder="Enter a secure password")
                
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", 
                                               placeholder="Re-enter your password")
                
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not new_username or not new_password:
                        st.warning("Please enter both username and password.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        with st.spinner("Creating your account..."):
                            success, message = register(new_username, new_password)
                            if success:
                                st.success(message)
                                # Switch to login mode after successful registration
                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error(message)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
else:
    # Custom CSS for styling
    st.markdown("""
        <style>
            .logout-container {
                position: absolute;
                top: 1px;
                right: 1px;
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: 1px;
            }
            .stButton > button {
                background-color: #FF4C4C;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 1px;
                padding: 0.1rem 0.1rem;
                cursor: pointer;
            }
            .stButton > button:hover {
                background-color: #FF2A2A;
            }
            .username-text {
                font-size: 0.1rem;
                margin-bottom: 1px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create some space at the top of the page
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # Create a container for the login info and logout button
    col1, col2 = st.columns([8, 1])

    with col2:
        # Display the username
        st.markdown(f"<div style='text-align: right;'>User: {st.session_state.username}</div>", unsafe_allow_html=True)
        
        # Add the logout button below
        if st.button("Logout", key="logout_button", help="Click to logout", use_container_width=True):
            logout()  # Make sure this function is defined
            st.rerun()
    # Main app code - only executed if authenticated
    st.title("🌴 Leave Visualization Dashboard")
    
    # User info  in the sidebar
    with st.sidebar:
        
        st.header("Filter Options")
        
        fiscal_years_df = load_fiscal_years()
        if not fiscal_years_df.empty:
            # Rest of your sidebar code remains the same
            fiscal_year_dict = dict(zip(fiscal_years_df['fiscal_year'], fiscal_years_df['fiscal_start_date'].astype(str) + ' - ' + fiscal_years_df['fiscal_end_date'].astype(str)))
            
            # Add "All" option to fiscal years
            fiscal_year_options = ["All"] + list(fiscal_year_dict.keys())
            selected_fiscal_year = st.selectbox("Select Fiscal Year", options=fiscal_year_options)

            if selected_fiscal_year == "All":
                start_date = pd.to_datetime(fiscal_years_df['fiscal_start_date'].min())
                end_date = pd.to_datetime(fiscal_years_df['fiscal_end_date'].max())
            else:
                fiscal_year_dates = fiscal_years_df[fiscal_years_df['fiscal_year'] == selected_fiscal_year].iloc[0]
                start_date = pd.to_datetime(fiscal_year_dates['fiscal_start_date'])
                end_date = pd.to_datetime(fiscal_year_dates['fiscal_end_date'])

            start_date = st.date_input("Start Date", start_date)
            end_date = st.date_input("End Date", end_date)
        else:
            start_date = datetime.now().date()
            end_date = datetime.now().date()
                
        leave_types_df = load_leave_types()
        
        # Initialize with default value
        selected_leave_type = "All"
        
        if not leave_types_df.empty:
            leave_type_dict = dict(zip(leave_types_df['id'], leave_types_df['leave_type']))
        
            # Add "All" option to leave types
            leave_type_options = [("All", "All")] + list(leave_type_dict.items())
            selected_leave_type = st.selectbox(
                "Select Leave Type",
                options=[id for id, _ in leave_type_options],
                format_func=lambda x: dict(leave_type_options)[x]
            )
        else:
            leave_type_dict = {}  # Initialize empty dict if no leave types loaded

        # Assuming the username is stored in session state
        if st.session_state.get("username") == "admin":
            # Display the Data Upload section only for the "admin"
            st.header("File Upload")
            if st.button("Upload New File"):
                st.session_state.show_file_upload = True
            else:
                st.session_state.show_file_upload = False

    # Create tabs - only if authenticated
    tab1, tab2, tab3 = st.tabs(["Overview", "Employee Analysis", "Today's Leaves"])

    if st.session_state.get('show_file_upload', False):
        with tab1:
            st.header("Load new file from device or drag it here")
            uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"], on_change=upload_file, key='file')
    else:
        # Load data based on selections
        selected_leave_type_id = None if selected_leave_type == "All" else selected_leave_type
        
        # Load data function with authentication
        df = load_data(start_date, end_date, selected_leave_type_id)

        def calculate_leave_days(df):
            if df.empty:
                return df
                
            if 'leave_days' not in df.columns:
                if 'start_date' in df.columns and 'end_date' in df.columns:
                    df['start_date'] = pd.to_datetime(df['start_date'])
                    df['end_date'] = pd.to_datetime(df['end_date'])
                    df['leave_days'] = (df['end_date'] - df['start_date']).dt.days + 1
                else:
                    st.error("Unable to calculate leave days. Missing required columns.")
            return df

        df = calculate_leave_days(df)
        
        # Custom CSS to improve the look and feel
        st.markdown("""
            <style>
            .main { padding: 2rem; }
            .stApp { background-color: #f0f2f6; }
            .metric-card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                padding: 1rem;
                height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .metric-label {
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #333;
            }
            </style>
        """, unsafe_allow_html=True)

        with tab1:
            st.header("Leave Overview")
            
            # Summary statistics
            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            if df is not None and not df.empty:
                with col1:
                    total_leave_days = df['leave_days'].sum() if 'leave_days' in df.columns else 'N/A'
                    st.markdown(f"""
                    <div class="metric-card" style="
                        background-color: white;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        padding: 1rem;
                        height: 100px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <p class="metric-label" style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                            Total Leave Days
                        </p>
                        <p class="metric-value" style="font-size: 1.5rem; font-weight: bold; color: #000;">
                            {total_leave_days}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    avg_leave_duration = df['leave_days'].mean() if 'leave_days' in df.columns else 'N/A'
                    avg_formatted = f"{avg_leave_duration:.1f} days" if isinstance(avg_leave_duration, float) else 'N/A'
                    st.markdown(f"""
                    <div class="metric-card" style="
                        background-color: white;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        padding: 1rem;
                        height: 100px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <p class="metric-label" style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                            Average Leave Duration
                        </p>
                        <p class="metric-value" style="font-size: 1.5rem; font-weight: bold; color: #000;">
                            {avg_formatted}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    total_employees_on_leave = df['employee_id'].nunique() if 'employee_id' in df.columns else 'N/A'
                    st.markdown(f"""
                    <div class="metric-card" style="
                        background-color: white;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        padding: 1rem;
                        height: 100px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <p class="metric-label" style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                            Total Employees on Leave
                        </p>
                        <p class="metric-value" style="font-size: 1.5rem; font-weight: bold; color: #000;">
                            {total_employees_on_leave}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    most_common_leave_type = 'N/A'
                    if 'leave_type_id' in df.columns and not df.empty:
                        most_common_id = df['leave_type_id'].mode().iloc[0]
                        most_common_leave_type = leave_type_dict.get(most_common_id, 'N/A')
                    
                    st.markdown(f"""
                    <div class="metric-card" style="
                        background-color: white;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        padding: 1rem;
                        height: 100px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <p class="metric-label" style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                            Most Common Leave Type
                        </p>
                        <p class="metric-value" style="font-size: 1.5rem; font-weight: bold; color: #000;">
                            {most_common_leave_type}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)


                # Visualizations
                st.subheader("Leave Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'leave_status' in df.columns and 'leave_days' in df.columns:
                        leave_status_chart = px.bar(
                            df.groupby('leave_status').agg({'leave_days': 'sum'}).reset_index(),
                            x='leave_status',
                            y='leave_days',
                            title='Total Leave Days by Status',
                            color='leave_status',
                            color_discrete_map={'APPROVED': 'green', 'REJECTED': 'red', 'Pending': 'yellow'},
                            height=450
                        )
                        leave_status_chart.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(leave_status_chart, use_container_width=True)

                with col2:
                    if 'leave_type' in df.columns:
                        leave_type_distribution = px.pie(
                            df,
                            names='leave_type',
                            title='Leave Type Distribution',
                            height=450
                        )
                        leave_type_distribution.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(leave_type_distribution, use_container_width=True)

                if 'start_date' in df.columns and 'leave_days' in df.columns:
                    leave_days_over_time = px.line(
                        df.groupby(pd.to_datetime(df['start_date']).dt.date).agg({'leave_days': 'sum'}).reset_index(),
                        x='start_date',
                        y='leave_days',
                        title='Leave Trends Over Time',
                        height=400
                    )
                    leave_days_over_time.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(leave_days_over_time, use_container_width=True)
            else:
                st.warning("No data available for the selected period or filters.")

        with tab2:
            st.header("Employee Leave Analysis")

            # Add CSS for improved selectbox appearance
            st.markdown("""
                <style>
                .employee-select-container {
                    margin-bottom: 20px;
                }
                .employee-select-label {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #333;
                }
                .stSelectbox > div > div {
                    border: 2px solid #ccc;
                    border-radius: 4px;
                    background-color: white;
                }
                .stSelectbox > div > div > div {
                    padding: 5px;
                }
                .stSelectbox [data-baseweb="select"] {
                    height: auto;
                }
                </style>
                """, unsafe_allow_html=True)
            
            if df is not None and not df.empty:
                emp_id_col = next((col for col in df.columns if 'employee_id' in col.lower()), None)
                emp_name_col = next((col for col in df.columns if 'employee_name' in col.lower()), None)
                
                if emp_id_col is None or emp_name_col is None:
                    st.error("Unable to identify employee ID and name columns. Please ensure your data includes these columns.")
                else:
                    employee_data = df[[emp_id_col, emp_name_col]].drop_duplicates()
                    employee_names = employee_data[emp_name_col].tolist()
                    employee_name_to_id = dict(zip(employee_data[emp_name_col], employee_data[emp_id_col]))

                    st.markdown('<div class="employee-select-container">', unsafe_allow_html=True)
                    st.markdown('<div class="employee-select-label">Select an Employee:</div>', unsafe_allow_html=True)
                    
                    # Handle empty employee list
                    if not employee_names:
                        st.warning("No employees found in the data for the selected period.")
                    else:
                        selected_employee_index = 0
                        if "selected_employee_name" in st.session_state and st.session_state.selected_employee_name in employee_names:
                            selected_employee_index = employee_names.index(st.session_state.selected_employee_name)
                            
                        st.session_state.selected_employee_name = st.selectbox(
                            "", 
                            options=employee_names, 
                            key="employee_select", 
                            label_visibility="collapsed",
                            index=selected_employee_index
                        )
                        selected_employee_name = st.session_state.selected_employee_name
                        st.markdown('</div>', unsafe_allow_html=True)

                        if selected_employee_name:
                            selected_employee_id = employee_name_to_id[selected_employee_name]
                            employee_df = df[df["employee_id"] == selected_employee_id]

                            if not employee_df.empty:
                                st.subheader(f"Leave Data for {selected_employee_name}")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                    if 'leave_type' in employee_df.columns:
                                        employee_leave_type = px.pie(
                                            employee_df,
                                            names='leave_type',
                                            title='Individual Leave Category Breakdown',
                                            height=400
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
                                            title='Individual Leave Status Overview',
                                            color='leave_status',
                                            color_discrete_map={'APPROVED': 'green', 'REJECTED': 'red', 'Pending': 'yellow'},
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
                                        title='Employee Leave History Timeline',
                                        height=400,
                                        labels={'leave_type': 'Leave Type'}
                                    )
                                    # Update x-axis to show only dates
                                    employee_leave_timeline.update_layout(margin=dict(l=20, r=20, t=40, b=20))
                                    st.plotly_chart(employee_leave_timeline, use_container_width=True)
                                else:
                                    st.warning("Required information for timeline chart is not available in the dataset.")
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.info(f"No leave data available for {selected_employee_name}.")
                        else:
                            st.info("Please select an employee to view their leave analysis.")
            else:
                st.warning("No data available for employee analysis.")

        with tab3:
            today = date.today()
            # Format the date
            formatted_today = today.strftime("%B %d, %Y")  # Example: "September 19, 2024"
            
            if df is not None and not df.empty:
                # Ensure dates are in consistent format
                df['start_date'] = pd.to_datetime(df['start_date']).dt.date
                df['end_date'] = pd.to_datetime(df['end_date']).dt.date
                today_leaves = df[(df['start_date'] <= today) & (df['end_date'] >= today)]
                
                if not today_leaves.empty:
                    # Create a more refined styled subheader with HTML and CSS
                    st.markdown(
                        f"""
                        <div style='
                            background-color: #f0f2f6; 
                            padding: 10px; 
                            border-radius: 10px; 
                            border: 1px solid #ddd;
                            text-align: center; 
                            font-family: "Roboto", sans-serif; 
                            color: #333;'>
                            <h3 style='margin: 0; font-size: 24px;'>Employees on Leave Today</h3>
                            <p style='font-size: 18px; color: #555;'>{formatted_today}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    for _, row in today_leaves.iterrows():
                        employee_name = row.get('employee_name', 'N/A')
                        leave_type_id = row.get('leave_type_id', 'N/A')
                        leave_type = row.get('leave_type', leave_type_dict.get(leave_type_id, 'N/A'))
                        leave_status = row.get('leave_status', 'N/A')
                        total_leave_days = row.get('leave_days', 'N/A')
                        
                        status_color = 'status-approved' if leave_status == 'APPROVED' else 'status-REJECTED' if leave_status == 'REJECTED' else ''
                    
                        st.markdown(f"""
                            <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: white;">
                                <h4>Employee Name: {employee_name}</h4>
                                <p>Leave Type: {leave_type}</p>
                                <p>Status: <span class="{status_color}">{leave_status}</span></p>
                                <p>Total Days: {total_leave_days}</p>
                            </div>
                        """, unsafe_allow_html=True)

                    # Summary of leaves by status
                    st.subheader("Today's Leave Summary")
                    status_counts = today_leaves['leave_status'].value_counts()
                    fig = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values, hole=.3)])
                    fig.update_layout(title_text="Leave Status Distribution")
                    st.plotly_chart(fig)
                else:
                    st.info("No employees are on leave today.")
            else:
                st.warning("No data available for today's leaves.")
