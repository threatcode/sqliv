# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Install system dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        git \
        python3-dev \
        libxml2-dev \
        libxslt-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /sqliv

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Clone and install SQLiv
RUN git clone https://github.com/threatcode/sqliv.git . && \
    python setup.py -i

# Create non-root user for security
RUN useradd -m sqliv && \
    chown -R sqliv:sqliv /sqliv

USER sqliv

# Set entrypoint
ENTRYPOINT ["python", "sqliv.py"]
CMD ["--help"]
