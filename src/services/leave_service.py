from src.db import db_engine
import pandas as pd

def find_leaves(start_date, end_date):
    # Query to fetch leave data within the selected date range
    query = f"""
    SELECT * FROM dbo.leave
    WHERE start_date BETWEEN '{start_date}' AND '{end_date}'
    """

    """Load data from the database based on a SQL query."""
    with db_engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df.to_dict()

def find_leave_types():
    # Fetch leave types from dbo.leave_type
    leave_types_query = """
    SELECT id, leave_type FROM dbo.leave_type
    """
    with db_engine.connect() as connection:
        df = pd.read_sql(leave_types_query,connection)
    return df.to_dict()

