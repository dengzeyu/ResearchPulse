FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files and source code for installation
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

# Install Python dependencies with arxiv support
RUN pip install --no-cache-dir ".[arxiv]"

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy remaining application files
COPY config/ ./config/
COPY templates/ ./templates/

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Set working directory to src for proper imports
WORKDIR /app/src

# Run the application
CMD ["python", "main.py"]
