import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_allocation_data():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Query to retrieve distinct allocation data where emp_id exists in dbo.employee
            allocation_query = """
            SELECT DISTINCT
                CAST(ad."id" AS INTEGER) AS id,  -- Adjust the casting if necessary
                ad."empId" AS emp_id,
                ad."name",
                ad."type"
            FROM raw.allocation_data ad
            """
            allocation_df = pd.read_sql(allocation_query, connection)

            for _, row in allocation_df.iterrows():
                upsert_allocation_query = """
                INSERT INTO dbo.allocation (id, emp_id, name, type)
                VALUES (:id, :emp_id, :name, :type)
                ON CONFLICT (id)
                DO UPDATE SET
                    emp_id = EXCLUDED.emp_id,
                    name = EXCLUDED.name,
                    type = EXCLUDED.type;
                """
                connection.execute(text(upsert_allocation_query), {
                    'id': row['id'],
                    'emp_id': row['emp_id'],
                    'name': row['name'],
                    'type': row['type']
                })

    print("Allocation data upserted successfully.")
