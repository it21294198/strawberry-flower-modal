FROM python:3.12-slim
# FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Copy application code and dependencies
# COPY ./requirements.txt ./requirements.txt
COPY ./requirements-windows.txt ./requirements.txt

# Debugging: Print the contents of requirements.txt
RUN cat requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application
COPY ./ ./

# Expose the application port
EXPOSE 80

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]