# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt


# Run app.py when the container launches
CMD ["python3", "main.py", "--log",  "true"]
