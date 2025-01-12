# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the app and requirements.txt to the container
COPY app.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8501

# Command to run the Streamlit app
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app/app.py" ]
