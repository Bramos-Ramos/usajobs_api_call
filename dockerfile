# Use the official Python image as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DB_HOST=<db-host>
ENV DB_NAME=<db-name>
ENV DB_USER=<db-user>
ENV DB_PASSWORD=<db-password>
ENV API_KEY=<api-key>
ENV API_EMAIL=<api-email>

# Run the command to start the application
CMD ["python", "etl_script.py"]
