import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_employee_leave_patterns():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Query to retrieve employee leave patterns
            leave_patterns_query = """
            SELECT
                ad."empId" AS emp_id,
                SUM(ad."leaveDays") AS total_leave_days,
                (
                    SELECT ad2."leaveType"
                    FROM raw.api_data ad2
                    WHERE ad2."empId" = ad."empId"
                    GROUP BY ad2."leaveType"
                    ORDER BY COUNT(ad2."leaveType") DESC
                    LIMIT 1
                ) AS leave_type_most_frequent,
                COUNT(ad."id") AS total_leaves_taken,
                CASE WHEN SUM(ad."leaveDays") > 0 THEN TRUE ELSE FALSE END AS has_taken_leave,
                AVG(ad."leaveDays") AS average_leave_days
            FROM raw.api_data ad
            GROUP BY ad."empId";
            """
            
            leave_patterns_df = pd.read_sql(leave_patterns_query, connection)

            for _, row in leave_patterns_df.iterrows():
                upsert_leave_patterns_query = """
                INSERT INTO dbo.employee_leave_patterns (
                    emp_id, total_leave_days, leave_type_most_frequent, total_leaves_taken, has_taken_leave, average_leave_days
                )
                VALUES (:emp_id, :total_leave_days, :leave_type_most_frequent, :total_leaves_taken, :has_taken_leave, :average_leave_days)
                ON CONFLICT (emp_id)
                DO UPDATE SET
                    total_leave_days = EXCLUDED.total_leave_days,
                    leave_type_most_frequent = EXCLUDED.leave_type_most_frequent,
                    total_leaves_taken = EXCLUDED.total_leaves_taken,
                    has_taken_leave = EXCLUDED.has_taken_leave,
                    average_leave_days = EXCLUDED.average_leave_days;
                """
                
                connection.execute(text(upsert_leave_patterns_query), {
                    'emp_id': row['emp_id'],
                    'total_leave_days': row['total_leave_days'],
                    'leave_type_most_frequent': row['leave_type_most_frequent'],
                    'total_leaves_taken': row['total_leaves_taken'],
                    'has_taken_leave': row['has_taken_leave'],
                    'average_leave_days': row['average_leave_days']
                })

    print("Employee leave patterns data upserted successfully.")
