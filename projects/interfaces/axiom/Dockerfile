# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend with pyproject.toml first for better caching
COPY backend/ ./backend/

# Install Python dependencies from backend directory
RUN cd backend && pip install --no-cache-dir -e .

# Copy frontend
COPY frontend/ ./frontend/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash axiom
RUN chown -R axiom:axiom /app
USER axiom

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]