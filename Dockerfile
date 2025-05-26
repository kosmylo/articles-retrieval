FROM python:3.10-slim

# Set working directory
WORKDIR /app

# System deps for PDF parsing, newspaper3k, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    poppler-utils \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create log & output dirs
RUN mkdir -p logs output

CMD ["python", "main.py"]