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

# Expose port 5000
EXPOSE 5000

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["/bin/sh","./entrypoint.sh"]