from src.db import db_engine
import pandas as pd

def find_fiscal_years():
    # Fetch fiscal years from dbo.fiscal
    fiscal_year_query="""
    SELECT fiscal_start_date, fiscal_end_date  from dbo.fiscal"""
    
    with db_engine.connect() as connection:
        df = pd.read_sql(fiscal_year_query,connection)
    return df.to_dict()