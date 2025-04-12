from typing import Optional, Dict, Any
import os
import jwt
import datetime
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import application services
from backend.data_ingestion.api_fetch import ingest_raw_data
from backend.transformation.dbo.transform import transform_data
from backend.services.leave_service import find_leaves, find_leave_types
from backend.services.upload_service import populate_from_file
from backend.services.fiscal_service import find_fiscal_years
from backend.services.employee_service import find_employee

# Access environment variables
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
API_ENDPOINT = os.getenv('API_ENDPOINT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port is 5432
DB_NAME = os.getenv('DB_NAME')

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

# Configuration for authentication
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database setup
DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define User model
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Models
class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    token: str
    token_type: str = "bearer"

class LoginForm(BaseModel):
    username: str
    password: str

class RegisterForm(BaseModel):
    username: str
    password: str

class MessageResponse(BaseModel):
    message: str

# Authentication helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user

# Create initial admin user at startup
@app.on_event("startup")
async def create_admin_user():
    db = SessionLocal()
    try:
        admin_user = get_user(db, "admin")
        if not admin_user:
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            new_admin = UserModel(
                username="admin",
                hashed_password=pwd_context.hash(admin_password)
            )
            db.add(new_admin)
            db.commit()
            logger.info("Admin user created")
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

# Routes for data ingestion and transformation
@app.post("/ingest")
async def api_fetch():
    ingest_raw_data()
    return {"message": "Raw data ingested"}

@app.post("/transform")
async def transform_raw_data():
    transform_data() 
    return {"message": "Raw data transformed"}

@app.get("/leaves")
async def get_leaves(start_date: str, end_date: str, leave_type: str|None=None):
    return find_leaves(start_date, end_date, leave_type)

@app.get("/leave-types")
async def get_leave_types():
    return find_leave_types()

@app.get("/fiscal-years")
async def get_fiscal_years():
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

@app.get("/profile", response_model=User)
async def get_profile(current_user: UserModel = Depends(get_current_user)):
    return {"username": current_user.username}

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