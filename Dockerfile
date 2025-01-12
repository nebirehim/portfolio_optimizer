FROM python:3.9-slim

# Install system dependencies for certain Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    gfortran

WORKDIR /app

# Copy the entire current directory (including app.py and requirements.txt) to the container
COPY . .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default port for Streamlit
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
