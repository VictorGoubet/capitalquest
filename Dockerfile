# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8051 available to the world outside this container
EXPOSE 8051

# Define environment variable
ENV PYTHONUNBUFFERED=1
ENV environment=prod

# Run app.py when the container launches
CMD ["python", "launch.py", "--env", "prod", "--component", "both"]