import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_designation_data():
    query = """
    SELECT DISTINCT 
        ad."designationId", 
        ad."designationName"
    FROM raw.api_data ad
    WHERE ad."designationName" IS NOT NULL;
    """
    
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            df = pd.read_sql(query, connection)

            for _, row in df.iterrows():
                upsert_query = """
                INSERT INTO dbo.designation (id, designation_name)
                VALUES (:designationId, :designationName)
                ON CONFLICT (id)
                DO UPDATE SET 
                    designation_name = EXCLUDED.designation_name;
                """
                connection.execute(text(upsert_query), {
                    'designationId': row['designationId'],
                    'designationName': row['designationName']
                })

    print("Designation data upserted successfully.")
