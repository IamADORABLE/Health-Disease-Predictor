FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port Flask will run on
EXPOSE 8000

# Run the app using Gunicorn (replace app:app with your filename:Flask instance)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
