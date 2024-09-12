import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_employee_data():
    query = """
    SELECT DISTINCT 
        ad."empId",
        ad."firstName",
        ad."middleName",
        ad."lastName",
        ad."email",
        ad."departmentDescription",
        ad."designationId",
        ad."isHr",
        ad."isSupervisor"
    FROM raw.api_data ad
    WHERE ad."empId" IS NOT NULL;
    """
    
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Fetch department descriptions and their IDs for mapping
            department_query = """
            SELECT department_description, id 
            FROM dbo.department;
            """
            department_df = pd.read_sql(department_query, connection)
            department_mapping = dict(zip(department_df['department_description'], department_df['id']))
            print(f"Department mapping: {department_mapping}")

            # Fetch API data
            df = pd.read_sql(query, connection)
            print(f"Fetched {len(df)} rows from raw.api_data.")

            for _, row in df.iterrows():
                department_id = department_mapping.get(row['departmentDescription'], None)
                
                upsert_query = """
                INSERT INTO dbo.employee (
                    emp_id, first_name, middle_name, last_name, email, department_id, designation_id, is_hr, is_supervisor
                ) VALUES (
                    :empId, :firstName, :middleName, :lastName, :email, 
                    :departmentId, :designationId, :isHr, :isSupervisor
                )
                ON CONFLICT (emp_id)
                DO UPDATE SET 
                    first_name = EXCLUDED.first_name,
                    middle_name = EXCLUDED.middle_name,
                    last_name = EXCLUDED.last_name,
                    email = EXCLUDED.email,
                    department_id = EXCLUDED.department_id,
                    designation_id = EXCLUDED.designation_id,
                    is_hr = EXCLUDED.is_hr,
                    is_supervisor = EXCLUDED.is_supervisor;
                """
                try:
                    connection.execute(text(upsert_query), {
                        'empId': row['empId'],
                        'firstName': row['firstName'],
                        'middleName': row['middleName'],
                        'lastName': row['lastName'],
                        'email': row['email'],
                        'departmentId': department_id,
                        'designationId': row['designationId'],
                        'isHr': row['isHr'],
                        'isSupervisor': row['isSupervisor']
                    })
                    print(f"Inserted/Updated employee ID: {row['empId']}")
                except Exception as e:
                    print(f"Error inserting/updating employee ID {row['empId']}: {e}")

    print("Employee data upserted successfully.")
