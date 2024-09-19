import pandas as pd
from sqlalchemy import text
from src.db import db_engine

def populate_fiscal_data():
    with db_engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Query to fetch distinct fiscal data
            fiscal_query = """
            SELECT DISTINCT
                ad."fiscalId" AS id,
                CAST(ad."fiscalStartDate" AS DATE) AS fiscal_start_date,
                CAST(ad."fiscalEndDate" AS DATE) AS fiscal_end_date,
                ad."fiscalIsCurrent"
            FROM raw.api_data ad;
            """
            fiscal_df = pd.read_sql(fiscal_query, connection)

            for _, row in fiscal_df.iterrows():
                # Insert data with conflict handling
                insert_fiscal_query = """
                INSERT INTO dbo.fiscal (id, fiscal_start_date, fiscal_end_date, fiscal_is_current)
                VALUES (:id, :fiscal_start_date, :fiscal_end_date, :fiscalIsCurrent)
                ON CONFLICT (fiscal_start_date, fiscal_end_date) DO NOTHING;
                """
                connection.execute(text(insert_fiscal_query), {
                    'id': row['id'],
                    'fiscal_start_date': row['fiscal_start_date'],
                    'fiscal_end_date': row['fiscal_end_date'],
                    'fiscalIsCurrent': row['fiscalIsCurrent']
                })

    print("Fiscal data processed successfully, no duplicates.")
