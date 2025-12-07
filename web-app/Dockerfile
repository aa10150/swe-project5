# web-app/Dockerfile
FROM python:3.10-slim

# Workdir inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Flask will listen on 5000
EXPOSE 5000

# Default: run the web app
CMD ["python", "run.py", "database/seed.py"]