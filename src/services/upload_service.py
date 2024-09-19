from src.data_ingestion.api_fetch import insert_data_to_db, create_schema
from src.transformation.dbo.transform import transform_data
from src.services.supabase import upload_file_to_supabase
import pandas as pd
from io import StringIO
import json


def extract_allocations(df):
    if 'allocations' not in df.columns:
        print("No 'allocations' column found in the data.")
        return pd.DataFrame()

    allocations_df_list = []
    for index, row in df.iterrows():
        allocations = row.get('allocations', None)
        emp_id = row.get('empId', None)  # Extract empId from the row
        if pd.notna(allocations):
            try:
                # Load the allocations data as a list of dictionaries
                allocations_data = json.loads(allocations)
                if isinstance(allocations_data, list):
                    # Convert each allocation dictionary to a DataFrame
                    normalized_data = pd.json_normalize(allocations_data)
                    # Add the empId to each record
                    normalized_data['empId'] = emp_id
                    allocations_df_list.append(normalized_data)
                else:
                    print(f"Invalid data format for allocations at row {index}: not a list.")
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                print(f"Error processing allocations for row {index}: {e}")
        else:
            print(f"No valid allocations data at row {index}")

    if allocations_df_list:
        return pd.concat(allocations_df_list, ignore_index=True)
    return pd.DataFrame()

    

async def populate_from_file(file):
    file_content = await file.read()
    upload_file_to_supabase(file.filename, file_content)
    csv_string = StringIO(file_content.decode("utf-8"))
    # Open a file at the defined path and write the contents of the uploaded file
    df = pd.read_csv(csv_string, sep='|')
    print(df)
    create_schema()
    insert_data_to_db(df, 'api_data', schema='raw')

     # Extract allocations data
    allocations_df = extract_allocations(df)

    print(allocations_df)

    # Insert allocations data into raw.allocation_data
    if not allocations_df.empty:
        # Ensure only the columns 'id', 'name', 'type', and 'empId' are present
        allocations_df = allocations_df[['id', 'name', 'type', 'empId']]
        insert_data_to_db(allocations_df, 'allocation_data', schema='raw')


    transform_data() 
    # return(file.filename)

