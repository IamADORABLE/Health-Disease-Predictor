# Use official Python 3.10 image
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy only requirements first for better Docker layer caching
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Then copy the rest of your app
COPY . /app/

# Expose Flask port
EXPOSE 5000

# Start the app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
