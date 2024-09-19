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
from fastapi import FastAPI,UploadFile,HTTPException
from src.data_ingestion.api_fetch import ingest_raw_data, insert_data_to_db, create_schema
from src.transformation.dbo.transform import transform_data
from src.services.leave_service import find_leaves, find_leave_types
from src.services.upload_service import populate_from_file
from src.services.fiscal_service import find_fiscal_years
from src.services.employee_service import find_employee
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/ingest")
async def api_fetch():
    ingest_raw_data()
    # new added
    # transform_data() 

    return {"message": "Raw data ingested"}

@app.post("/transform")
async def transform_raw_data():
    # ingest_raw_data()
    # new added
    transform_data() 
    return {"message": "Raw data transformed"}

@app.get("/leaves")
async def get_leaves(start_date: str , end_date: str , leave_type: str):
    return find_leaves(start_date, end_date, leave_type)

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

# @app.get("/employee/{emp_id}")
# async def get_employee(emp_id: int):
#     print (emp_id)
#     return find_employee(emp_id)

@app.get("/employee/{emp_id}")
async def get_employee(emp_id: int):
    try:
        data = find_employee(emp_id)
        if data is None:
            raise HTTPException(status_code=500, detail="Failed to fetch employee details")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/employee/{emp_id}")
# async def get_employee(emp_id: int):
#     result = find_employee(emp_id)
    
#     if "error" in result:
#         raise HTTPException(status_code=500, detail=result["error"])
    
#     return result

@app.post("/upload")
async def upload_file(file: UploadFile):
    await populate_from_file(file)

