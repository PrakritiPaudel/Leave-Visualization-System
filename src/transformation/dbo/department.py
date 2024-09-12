import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_department_data():
    query = """
    SELECT DISTINCT 
        ad."departmentDescription"
    FROM raw.api_data ad
    WHERE ad."departmentDescription" IS NOT NULL;
    """
    
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            df = pd.read_sql(query, connection)

            for _, row in df.iterrows():
                upsert_query = """
                INSERT INTO dbo.department (department_description)
                VALUES (:departmentDescription)
                ON CONFLICT DO NOTHING;
                """
                connection.execute(text(upsert_query), {
                    'departmentDescription': row['departmentDescription']
                })

    print("Department data upserted successfully.")
