from src.db import db_engine
import pandas as pd

def find_leaves(start_date, end_date, leave_type_id):
    # Query to fetch leave data within the selected date range
    query = f"""
    SELECT l.employee_id, e.first_name, e.last_name, CONCAT(first_name,' ',last_name) as employee_name,  d2.designation_name, d.department_description,
             l.start_date, l.end_date, lt.leave_type,l.leave_status ,l.leave_days ,l.reason ,l.leave_type_id ,l.fiscal_id ,l.is_automated ,l.is_converted 
      FROM dbo.employee e
      LEFT JOIN dbo.department d ON d.id = e.department_id  
      LEFT JOIN dbo.designation d2 ON d2.id = e.designation_id 
      LEFT JOIN dbo.allocation a ON a.emp_id = e.emp_id 
      LEFT JOIN dbo.leave l ON l.employee_id = e.emp_id 
      LEFT JOIN dbo.leave_type lt ON l.leave_type_id = lt.id 
    WHERE start_date BETWEEN '{start_date}' AND '{end_date}' and l.leave_type_id = '{leave_type_id}'
    """

    """Load data from the database based on a SQL query."""
    with db_engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df.to_dict()

def find_leave_types():
    # Fetch leave types from dbo.leave_type
    leave_types_query = """
    SELECT id, leave_type FROM dbo.leave_type
    """
    with db_engine.connect() as connection:
        df = pd.read_sql(leave_types_query,connection)
    return df.to_dict()

