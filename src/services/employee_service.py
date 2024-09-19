from src.db import db_engine
import pandas as pd

def find_employee(emp_id):
    # Define the SQL query with a parameter placeholder for emp_id
    employee_query = f"""
      SELECT e.emp_id, e.first_name, e.last_name, CONCAT(first_name,' ',last_name) as employee_name,  d2.designation_name, d.department_description,
             l.start_date, l.end_date, lt.leave_type,l.leave_status 
      FROM dbo.employee e
      LEFT JOIN dbo.department d ON d.id = e.department_id  
      LEFT JOIN dbo.designation d2 ON d2.id = e.designation_id 
      LEFT JOIN dbo.allocation a ON a.emp_id = e.emp_id 
      LEFT JOIN dbo.leave l ON l.employee_id = e.emp_id 
      LEFT JOIN dbo.leave_type lt ON l.leave_type_id = lt.id
      WHERE e.emp_id = %(emp_id)s
    """
    #   
    # # Execute the query with emp_id as a parameter
    # with db_engine.connect() as connection:
    #     df = pd.read_sql(fiscal_year_query, connection, params={"emp_id": emp_id})
    
    # return df.to_dict()
    
    try:
        # Execute the query with emp_id as a parameter
        with db_engine.connect() as connection:
            df = pd.read_sql(employee_query, connection, params={'emp_id': str(emp_id)})
        
        if df.empty:
            return {"error": "No data found for this employee"}

        return df.to_dict()  # Use 'records' to get a list of dicts
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
