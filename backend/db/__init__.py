import os
from sqlalchemy import create_engine, text

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port is 5432
DB_NAME = os.getenv('DB_NAME')

# Create a database connection URL
DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create a database engine
db_engine = create_engine(DATABASE_URL)
