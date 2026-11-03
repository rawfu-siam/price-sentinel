# Production Dockerfile for Price Sentinel E-Commerce Monitor
# Utilizing official Playwright Python image for reliable Chromium binary support
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory inside container
WORKDIR /app

# Set environment variables for clean python execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure exact Playwright browser binaries and OS dependencies are installed
RUN playwright install --with-deps chromium

# Copy application source code into the container (respecting .dockerignore)
COPY . .

# Expose port for FastAPI service
EXPOSE 8000

# Run Uvicorn server bound to host interface
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
