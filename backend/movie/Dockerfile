FROM python:3.11-slim

WORKDIR /app

COPY movie/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY movie/ ./movie/
COPY monorepo/ ./monorepo/

CMD ["uvicorn", "movie.main:app", "--host", "0.0.0.0", "--port", "8002"]
