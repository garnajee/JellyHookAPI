# Use a lightweight Python image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and data
COPY . .

# Expose the port Jellyfin would use
EXPOSE 8096

# Command to run the application
CMD ["python", "app.py"]
