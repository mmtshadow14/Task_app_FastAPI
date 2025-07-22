# Use an official Python runtime as a parent image
FROM python:3.13

# Set the working directory in the container
WORKDIR /src

# Copy requirements file
COPY requirements.txt /src/

# Install project dependencies
RUN pip install -U pip
RUN pip install -r requirements.txt


# Copy the rest of the application code
COPY . /src/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with fastapi dev
CMD ["fastapi", "dev", "main.py"]