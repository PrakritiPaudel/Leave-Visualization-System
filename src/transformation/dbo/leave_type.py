import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_leave_type_data():
    with db_engine.connect() as connection:
        with connection.begin():
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

            leave_type_df = leave_type_df.drop_duplicates(subset=['leaveTypeId', 'leaveType'])

            for _, row in leave_type_df.iterrows():
                upsert_leave_type_query = """
                WITH new_values (id, leave_type, default_days, transferable_days, is_consecutive) AS (
                    VALUES (:leaveTypeId, :leaveType, :defaultDays, :transferableDays, :is_consecutive)
                ),
                upsert AS (
                    UPDATE dbo.leave_type lt
                    SET 
                        default_days = nv.default_days,
                        transferable_days = nv.transferable_days,
                        is_consecutive = nv.is_consecutive
                    FROM new_values nv
                    WHERE (lt.id = nv.id) OR (lt.leave_type = nv.leave_type)
                    RETURNING lt.*
                )
                INSERT INTO dbo.leave_type (id, leave_type, default_days, transferable_days, is_consecutive)
                SELECT id, leave_type, default_days, transferable_days, is_consecutive
                FROM new_values
                WHERE NOT EXISTS (SELECT 1 FROM upsert u WHERE u.id = new_values.id OR u.leave_type = new_values.leave_type);
                """
                connection.execute(text(upsert_leave_type_query), {
                    'leaveTypeId': row['leaveTypeId'],
                    'leaveType': row['leaveType'],
                    'defaultDays': row['defaultDays'],
                    'transferableDays': row['transferableDays'],
                    'is_consecutive': row['is_consecutive']
                })

    print("Leave type data upserted successfully.")