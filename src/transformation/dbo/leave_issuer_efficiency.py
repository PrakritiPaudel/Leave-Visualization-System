import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_leave_issuer_efficiency():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Query to retrieve leave issuer efficiency data
            leave_issuer_efficiency_query = """
            SELECT
                ad."leaveIssuerId" AS leave_issuer_id,
                COUNT(ad."id") AS total_leaves_processed,
                AVG(EXTRACT(EPOCH FROM (ad."updatedAt"::TIMESTAMP - ad."createdAt"::TIMESTAMP)) / 3600) AS average_response_time,
                SUM(CASE WHEN ad."leaveStatus" = 'approved' THEN 1 ELSE 0 END) / COUNT(ad."id")::FLOAT AS approval_rate,
                SUM(CASE WHEN ad."leaveStatus" = 'rejected' THEN 1 ELSE 0 END) / COUNT(ad."id")::FLOAT AS rejection_rate
            FROM
                raw.api_data ad
            WHERE
                ad."leaveIssuerId" IS NOT NULL
            GROUP BY
                ad."leaveIssuerId";
            """
            
            leave_issuer_efficiency_df = pd.read_sql(leave_issuer_efficiency_query, connection)

            for _, row in leave_issuer_efficiency_df.iterrows():
                upsert_leave_issuer_efficiency_query = """
                INSERT INTO dbo.leave_issuer_efficiency (
                    leave_issuer_id, total_leaves_processed, average_response_time, approval_rate, rejection_rate
                )
                VALUES (:leave_issuer_id, :total_leaves_processed, :average_response_time, :approval_rate, :rejection_rate)
                ON CONFLICT (leave_issuer_id)
                DO UPDATE SET
                    total_leaves_processed = EXCLUDED.total_leaves_processed,
                    average_response_time = EXCLUDED.average_response_time,
                    approval_rate = EXCLUDED.approval_rate,
                    rejection_rate = EXCLUDED.rejection_rate;
                """
                
                connection.execute(text(upsert_leave_issuer_efficiency_query), {
                    'leave_issuer_id': row['leave_issuer_id'],
                    'total_leaves_processed': row['total_leaves_processed'],
                    'average_response_time': row['average_response_time'],
                    'approval_rate': row['approval_rate'],
                    'rejection_rate': row['rejection_rate']
                })

    print("Leave issuer efficiency data upserted successfully.")
