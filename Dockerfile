FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

#Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copying all files from the current directory to the /app directory in the container
COPY . .

#Run setup.py to install the package
RUN pip install --no-cache-dir -e .

#used port 5000 for the application
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]


