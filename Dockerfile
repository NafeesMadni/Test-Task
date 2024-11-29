# Use the official Python image
FROM python:3.10-alpine3.15

# Set the working directory in the container
WORKDIR /app

# Copy application files to the container
COPY . /app/

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "FlaskRESTful.py"]
