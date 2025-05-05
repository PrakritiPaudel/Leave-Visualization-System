from typing import Dict, Optional, Any
import os
import datetime
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

# Import application services
from backend.data_ingestion.api_fetch import ingest_raw_data
from backend.transformation.dbo.transform import transform_data
from backend.services.leave_service import find_leaves, find_leave_types
from backend.services.upload_service import populate_from_file
from backend.services.fiscal_service import find_fiscal_years
from backend.services.employee_service import find_employee

# Import authentication module
from backend.services.auth import (
    User, Token, LoginForm, RegisterForm, MessageResponse,
    authenticate_user, create_access_token, get_user, pwd_context,
    get_current_user, create_admin_user,
    get_db, UserModel, ACCESS_TOKEN_EXPIRE_MINUTES,get_admin_user
)

# Initialize FastAPI app
app = FastAPI(title="Leave Management API")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

# Configuration for API endpoint
api_endpoint = os.getenv('API_ENDPOINT', 'http://localhost:8000')

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production to restrict origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Create initial admin user at startup
# @app.on_event("startup")
# async def initialize_admin():
#     await create_admin_user()

# Routes for data ingestion and transformation
@app.post("/ingest")
# async def api_fetch(current_user: UserModel = Depends(get_admin_user)):
async def api_fetch():
    ingest_raw_data()
    return {"message": "Raw data ingested"}

@app.post("/transform")
# async def transform_raw_data(current_user: UserModel = Depends(get_admin_user)):
async def transform_raw_data():
    transform_data() 
    return {"message": "Raw data transformed"}

@app.get("/leaves")
async def get_leaves(
    start_date: str,
    end_date: str,
    leave_type: str | None = None,
    current_user: UserModel = Depends(get_current_user)
):
    return find_leaves(start_date, end_date, leave_type)

@app.get("/leave-types")
async def get_leave_types(current_user: UserModel = Depends(get_current_user)):
    return find_leave_types()

@app.get("/fiscal-years")
async def get_fiscal_years(current_user: UserModel = Depends(get_current_user)):
    return find_fiscal_years()

# Routes for authentication and user management
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: LoginForm, db = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=MessageResponse)
async def register_user(form_data: RegisterForm, db = Depends(get_db)):
    user_exists = get_user(db, form_data.username)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    new_user = UserModel(
        username=form_data.username,
        hashed_password=pwd_context.hash(form_data.password)
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User created successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# @app.get("/profile", response_model=User)
# async def get_profile(current_user: UserModel = Depends(get_current_user)):
#     return {"username": current_user.username}

# added for upload functionality
@app.get("/user-profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Return detailed user profile information including admin status"""
    return {
        "username": current_user.username,
        "is_admin": current_user.is_admin, 
        "id": current_user.id
    }
    print ('admingggggggg',is_admin)

@app.post("/upload", response_model=MessageResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user)
):
    # Process the file
    await populate_from_file(file)
    return {"message": "File uploaded successfully"}

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    return {"status": "healthy"}

# Main entry point for the application
if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)