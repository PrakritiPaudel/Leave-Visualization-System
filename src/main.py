# from fastapi import FastAPI
# from .data_ingestion.api_fetch import ingest_raw_data
# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# @app.post("/apifetch")
# async def api_fetch():
#     ingest_raw_data()
#     return {"message": "Raw data ingested"}

from typing import Optional
from fastapi import FastAPI,UploadFile
from src.data_ingestion.api_fetch import ingest_raw_data, insert_data_to_db, create_schema
from src.transformation.dbo.transform import transform_data
from src.services.leave_service import find_leaves, find_leave_types
from src.services.upload_service import populate_from_file
from src.services.fiscal_service import find_fiscal_years
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/apifetch")
async def api_fetch():
    ingest_raw_data()
    # new added
    transform_data() 

    return {"message": "Raw data ingested and transformed"}

@app.get("/leaves")
async def get_leaves(start_date: str , end_date: str ):
    return find_leaves(start_date, end_date)

@app.get("/leave-types")
async def get_leave_types():
    return find_leave_types()

# @app.post("/runmigrations")
# async def migrate():
#     run_migrations()
#     return {"message": "Migrations executed successfully"}

@app.get("/fiscal-years")
async def get_fiscal_years():
    return find_fiscal_years()

@app.post("/upload")
async def upload_file(file: UploadFile):
    await populate_from_file(file)
    return 'Hello World'
    # file_path = os.path.join(file.filename)
    # print(file_path)
    
    # # Open a file at the defined path and write the contents of the uploaded file
    # df = pd.read_csv(file_path, sep='|')
    # create_schema()
    # insert_data_to_db(df, 'api_data', schema='raw')

    #  # Extract allocations data
    # allocations_df = extract_allocations(df)

    # print(allocations_df)

    # # Insert allocations data into raw.allocation_data
    # if not allocations_df.empty:
    #     # Ensure only the columns 'id', 'name', 'type', and 'empId' are present
    #     allocations_df = allocations_df[['id', 'name', 'type', 'empId']]
    #     insert_data_to_db(allocations_df, 'allocation_data', schema='raw')


    # transform_data() 
    # print(df)
    # return(file.filename)
