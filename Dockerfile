# Docker image for SweCli
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install MCP Azure DevOps server
RUN npm install -g @azure-devops/mcp

# Copy application code
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash swecli
USER swecli

# Set up working directory for code generation
WORKDIR /workspace

# Default command
ENTRYPOINT ["swecli"]
CMD ["--help"]
