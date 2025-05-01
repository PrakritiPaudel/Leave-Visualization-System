from typing import Optional, List
import os
import jwt
import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, Session
import logging

# Import database engine from existing module
from backend.db import db_engine

# Set up logging
logger = logging.getLogger("auth")

# Configuration for authentication
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Create Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# Create base model
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define User model - Adding is_admin field
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)  # Add admin role flag

# Create tables
Base.metadata.create_all(bind=db_engine)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# API Models
class User(BaseModel):
    username: str
    is_admin: bool = False

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

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# Add a new dependency for checking admin privileges
async def get_admin_user(current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation",
        )
    return current_user

# Initialize admin user function - Updated to set is_admin flag
# Initialize admin user function - Updated to handle password securely
async def create_admin_user():
    db = SessionLocal()
    try:
        admin_user = get_user(db, "admin") 
        
        # Get admin credentials from environment variables
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        if not admin_password:
            logger.warning("ADMIN_PASSWORD environment variable not set. Admin user creation skipped.")
            return
            
        if not admin_user:
            new_admin = UserModel(
                username=admin_username,
                hashed_password=pwd_context.hash(admin_password),
                is_admin=True
            )
            db.add(new_admin)
            db.commit()
            logger.info(f"Admin user '{admin_username}' created successfully")
        elif not admin_user.is_admin:
            # Ensure existing admin user has admin privileges
            admin_user.is_admin = True
            db.commit()
            logger.info(f"Updated user '{admin_username}' with admin privileges")
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
    finally:
        db.close()