import requests
import os
import json
from fastapi import FastAPI
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
dotenv_path = '.env'
load_dotenv(dotenv_path)

# Access environment variables
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
API_ENDPOINT = os.getenv('API_ENDPOINT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port is 5432
DB_NAME = os.getenv('DB_NAME')

# Check if variables are loaded correctly
if not BEARER_TOKEN or not API_ENDPOINT:
    raise ValueError("Missing environment variables. Ensure .env file is correctly configured.")

headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}' if BEARER_TOKEN else None
}

# Create a database connection URL
DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create a database engine
engine = create_engine(DATABASE_URL)

# Create the 'raw' schema if it doesn't exist
def create_schema():
    try:
        with engine.connect() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
            connection.commit()
        print("Schema 'raw' created or already exists.")
    except SQLAlchemyError as e:
        print(f"Error creating schema 'raw': {str(e)}")

def ingest_api_data(API_ENDPOINT, headers):
    all_data = []
    page = 1
    while True:
        params = {'page': page}
        try:
            response = requests.get(API_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data['data'])
            if not data.get('next_page'):
                break
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data from page {page}. Status code: {response.status_code} - {e}")
            break
    return all_data

def insert_data_to_db(df, table_name, schema='raw'):
    try:
        df.to_sql(table_name, engine, schema=schema, if_exists='replace', index=False)
        print(f"Data inserted into PostgreSQL table '{schema}.{table_name}' successfully.")
    except SQLAlchemyError as e:
        print(f"Error inserting data into PostgreSQL table '{schema}.{table_name}': {str(e)}")

def parse_json_and_insert(api_data):
    main_data = []
    nested_data = []
    for entry in api_data:
        main_entry = entry.copy()
        allocations = main_entry.pop('allocations', None)
        if allocations is not None and isinstance(allocations, list):
            main_entry['allocations'] = json.dumps(allocations)
            for alloc_item in allocations:
                nested_entry = {'empId': main_entry['empId']}
                nested_entry.update(alloc_item)
                nested_data.append(nested_entry)
        main_data.append(main_entry)
    
    df_main = pd.DataFrame(main_data)
    df_nested = pd.DataFrame(nested_data)
    print(df_nested)

    insert_data_to_db(df_main, 'api_data', schema='raw')
    insert_data_to_db(df_nested, 'allocation_data', schema='raw')


def ingest_raw_data():
    create_schema()  # Ensure schema is created before ingesting data
    api_data = ingest_api_data(API_ENDPOINT, headers)
    if api_data:
        parse_json_and_insert(api_data)
    
        # raw ingest done
    else:
        print("No data fetched from API.")

if __name__ == "__main__":
    ingest_raw_data()
