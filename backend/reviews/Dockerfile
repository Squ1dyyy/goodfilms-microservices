FROM python:3.11-slim

WORKDIR /app

COPY reviews/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reviews/ ./reviews/
COPY monorepo/ ./monorepo/

CMD ["uvicorn", "reviews.main:app", "--host", "0.0.0.0", "--port", "8005"]
