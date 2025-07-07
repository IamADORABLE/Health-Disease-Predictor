# Use official Python 3.10 image
FROM python:3.10

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (default Flask port)
EXPOSE 5000

# Start the app (change 'app' if needed)
CMD ["gunicorn", "app:app"]
