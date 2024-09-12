# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /myapp

# Install PostgreSQL development libraries
RUN apt-get update --fix-missing && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean
    
COPY requirements.txt /myapp/

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Install dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . /myapp


# # Copy the .env file into the container
# COPY .env /myapp/.env

# Expose port 5000
EXPOSE 5000
# TODO
# migration run vaesi blla app up grne

# Run the API fetch script
# CMD ["fastapi", "run", "src/main.py", "--port", "5000"]
# RUN chown root:root ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["/bin/sh","./entrypoint.sh"]
# CMD ["python", "src/data_ingestion/api_fetch.py"]
# Expose port 8501 for Streamlit
# EXPOSE 8501

# Run Streamlit app by default
# CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

#different docker file for fast api and dashboard TODO
