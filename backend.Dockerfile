FROM python:3.10-slim

# Install system dependencies (C++ compiler for mcp_tools/builder.py)
RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pybind11

# Copy project files
COPY . .

# Try to pre-build the core C++ extension
RUN cd core && python setup.py build_ext --inplace || true

# Expose backend port
EXPOSE 8000

# Run FastAPI server
CMD ["python", "web/backend/api.py"]
