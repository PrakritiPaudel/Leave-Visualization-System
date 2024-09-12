import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_leave_type_data():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Populate the leave_type table
            leave_type_query = """
            SELECT DISTINCT
                ad."leaveTypeId",
                ad."leaveType",
                ad."defaultDays",
                ad."transferableDays",
                CASE WHEN ad."isConsecutive" = 1 THEN TRUE ELSE FALSE END AS is_consecutive
            FROM raw.api_data ad;
            """
            leave_type_df = pd.read_sql(leave_type_query, connection)

            for _, row in leave_type_df.iterrows():
                upsert_leave_type_query = """
                INSERT INTO dbo.leave_type (id, leave_type, default_days, transferable_days, is_consecutive)
                VALUES (:leaveTypeId, :leaveType, :defaultDays, :transferableDays, :is_consecutive)
                ON CONFLICT (id)
                DO UPDATE SET
                    leave_type = EXCLUDED.leave_type,
                    default_days = EXCLUDED.default_days,
                    transferable_days = EXCLUDED.transferable_days,
                    is_consecutive = EXCLUDED.is_consecutive;
                """
                connection.execute(text(upsert_leave_type_query), {
                    'leaveTypeId': row['leaveTypeId'],
                    'leaveType': row['leaveType'],
                    'defaultDays': row['defaultDays'],
                    'transferableDays': row['transferableDays'],
                    'is_consecutive': row['is_consecutive']
                })

    print("Leave type data upserted successfully.")
