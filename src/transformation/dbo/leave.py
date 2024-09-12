from sqlalchemy import text
from src.db import db_engine
import pandas as pd

def populate_leave_data():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Fetch existing employees
            employees_query = "SELECT emp_id FROM dbo.employee"
            employees_df = pd.read_sql(employees_query, connection)
            employee_ids = set(employees_df['emp_id'])

            # Populate the leave table
            leave_query = """
            SELECT DISTINCT
                CAST(ad."empId" AS VARCHAR(50)) AS employee_id,
                CAST(ad."startDate" AS DATE) AS start_date,
                CAST(ad."endDate" AS DATE) AS end_date,
                ad."leaveDays",
                ad."reason",
                ad."leaveStatus",
                ad."status",
                ad."responseRemarks",
                ad."leaveTypeId",
                f.id AS fiscal_id,
                CURRENT_TIMESTAMP AS created_at,
                CURRENT_TIMESTAMP AS updated_at,
                CASE 
                    WHEN ad."isAutomated" = 1 THEN TRUE
                    ELSE FALSE
                END AS is_automated,
                CASE 
                    WHEN ad."isConverted" = 1 THEN TRUE
                    ELSE FALSE
                END AS is_converted
            FROM raw.api_data ad
            LEFT JOIN dbo.fiscal f ON CAST(f.fiscal_start_date AS DATE) = CAST(ad."fiscalStartDate" AS DATE) 
                AND CAST(f.fiscal_end_date AS DATE) = CAST(ad."fiscalEndDate" AS DATE);
            """
            leave_df = pd.read_sql(leave_query, connection)
            print(leave_df)

            # Filter out rows with non-existent employee IDs
            leave_df = leave_df[leave_df['employee_id'].isin(employee_ids)]
            print(2,employee_ids)
            print(3, leave_df)
            for _, row in leave_df.iterrows():
                upsert_leave_query = """
                INSERT INTO dbo.leave (
                    employee_id, start_date, end_date, leave_days, reason, leave_status, status, 
                    response_remarks, leave_type_id, fiscal_id, created_at, updated_at, is_automated, is_converted
                )
                VALUES (
                    :employee_id, :start_date, :end_date, :leave_days, :reason, :leave_status, :status,
                    :response_remarks, :leave_type_id, :fiscal_id, :created_at, :updated_at, :is_automated, :is_converted
                )
                ON CONFLICT (employee_id, start_date, end_date)
                DO UPDATE SET
                    leave_days = EXCLUDED.leave_days,
                    reason = EXCLUDED.reason,
                    leave_status = EXCLUDED.leave_status,
                    status = EXCLUDED.status,
                    response_remarks = EXCLUDED.response_remarks,
                    leave_type_id = EXCLUDED.leave_type_id,
                    fiscal_id = EXCLUDED.fiscal_id,
                    updated_at = EXCLUDED.updated_at,
                    is_automated = EXCLUDED.is_automated,
                    is_converted = EXCLUDED.is_converted;
                """
                connection.execute(text(upsert_leave_query), {
                    'employee_id': row['employee_id'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'leave_days': row['leaveDays'],
                    'reason': row['reason'],
                    'leave_status': row['leaveStatus'],
                    'status': row['status'],
                    'response_remarks': row['responseRemarks'],
                    'leave_type_id': row['leaveTypeId'],
                    'fiscal_id': row['fiscal_id'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'is_automated': row['is_automated'],
                    'is_converted': row['is_converted']
                })

    print("Leave data upserted successfully.")
