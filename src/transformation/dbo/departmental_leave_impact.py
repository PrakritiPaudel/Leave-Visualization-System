import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_departmental_leave_impact():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Query to retrieve and aggregate data for departmental leave impact
            impact_query = """
            SELECT
                ad."departmentDescription" AS department_description,
                COUNT(DISTINCT ad."empId") AS total_employees_on_leave,
                AVG(ad."leaveDays") AS average_leave_duration,
                SUM(ad."leaveDays") AS total_leave_days,
                SUM(ad."leaveDays") / COUNT(DISTINCT ad."empId")::FLOAT AS impact_score
            FROM
                raw.api_data ad
            GROUP BY
                ad."departmentDescription";
            """
            impact_df = pd.read_sql(impact_query, connection)

            for _, row in impact_df.iterrows():
                upsert_impact_query = """
                INSERT INTO dbo.departmental_leave_impact (
                    department_description, total_employees_on_leave, average_leave_duration, total_leave_days, impact_score
                )
                VALUES (
                    :department_description, :total_employees_on_leave, :average_leave_duration, :total_leave_days, :impact_score
                )
                ON CONFLICT (department_description)
                DO UPDATE SET
                    total_employees_on_leave = EXCLUDED.total_employees_on_leave,
                    average_leave_duration = EXCLUDED.average_leave_duration,
                    total_leave_days = EXCLUDED.total_leave_days,
                    impact_score = EXCLUDED.impact_score;
                """
                connection.execute(text(upsert_impact_query), {
                    'department_description': row['department_description'],
                    'total_employees_on_leave': row['total_employees_on_leave'],
                    'average_leave_duration': row['average_leave_duration'],
                    'total_leave_days': row['total_leave_days'],
                    'impact_score': row['impact_score']
                })

    print("Departmental leave impact data upserted successfully.")
