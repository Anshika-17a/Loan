# Use a Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This layer is often cached, speeding up builds if requirements don't change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY ./app /app/app

# Command to run the application (will be customized later)
# This uses uvicorn to serve the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Expose the port the app runs on
EXPOSE 8000