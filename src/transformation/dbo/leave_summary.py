import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_leave_summary_data():
    query = """
    SELECT 
        ad."departmentDescription",
        ad."designationName",
        ad."leaveType",
        SUM(ad."leaveDays") AS total_leave_days,
        AVG(ad."leaveDays") AS average_leave_days_per_employee,
        COUNT(DISTINCT ad."empId") AS total_employees,
        CONCAT(ad."fiscalStartDate", ' - ', ad."fiscalEndDate") AS fiscal_year
    FROM 
        raw.api_data ad
    GROUP BY 
        ad."departmentDescription", ad."designationName", ad."leaveType", fiscal_year;
    """
    
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            df = pd.read_sql(query, connection)

            for _, row in df.iterrows():
                upsert_query = """
                INSERT INTO dbo.leave_summary (
                    department_description, designation_name, leave_type, total_leave_days, 
                    average_leave_days_per_employee, total_employees, fiscal_year
                )
                VALUES (
                    :departmentDescription, :designationName, :leaveType, :total_leave_days,
                    :average_leave_days_per_employee, :total_employees, :fiscal_year
                )
                ON CONFLICT (department_description, designation_name, leave_type, fiscal_year)
                DO UPDATE SET 
                    total_leave_days = EXCLUDED.total_leave_days,
                    average_leave_days_per_employee = EXCLUDED.average_leave_days_per_employee,
                    total_employees = EXCLUDED.total_employees;
                """
                connection.execute(text(upsert_query), {
                    'departmentDescription': row['departmentDescription'],
                    'designationName': row['designationName'],
                    'leaveType': row['leaveType'],
                    'total_leave_days': row['total_leave_days'],
                    'average_leave_days_per_employee': row['average_leave_days_per_employee'],
                    'total_employees': row['total_employees'],
                    'fiscal_year': row['fiscal_year']
                })

    print("Leave summary data upserted successfully.")
