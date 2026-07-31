# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /backend

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install torch CPU and dependencies in a single step to force CPU version usage
COPY recomendations/requirements.txt ./recomendations/requirements.txt
RUN pip install --no-cache-dir torch -r recomendations/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Stage 2: Final runtime stage
FROM python:3.11-slim AS runner

WORKDIR /backend

# Copy installed libraries from builder stage (build dependencies are discarded)
COPY --from=builder /usr/local /usr/local

ENV PYTHONPATH=/backend

# Copy application files
COPY monorepo ./monorepo
COPY recomendations ./recomendations
COPY movie/models ./movie/models
COPY movie/models/base.py ./movie/models/base.py

CMD ["uvicorn", "recomendations.main:app", "--host", "0.0.0.0", "--port", "8006"]
