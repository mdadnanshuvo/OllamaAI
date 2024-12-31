# Base Python Image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for PostgreSQL and PostGIS
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc\
    binutils \
    gdal-bin \
    libproj-dev \
    && apt-get clean


    

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Copy the SQL file into the container
COPY /app/Data_Parsing/tripcom_backup_20241230123803.sql /app/Data_Parsing/




# Set the correct permissions for the SQL file
RUN chmod 644 /app/Data_Parsing/tripcom_backup_20241230123803.sql

# Expose port 8000
EXPOSE 8000



# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
