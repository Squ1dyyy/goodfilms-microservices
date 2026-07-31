FROM python:3.11-slim

WORKDIR /app

COPY admin/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY admin/ ./admin/
COPY auth/ ./auth/
COPY movie/ ./movie/
COPY users/ ./users/
COPY notifications/ ./notifications/
COPY monorepo/ ./monorepo/

CMD ["uvicorn", "admin.main:app", "--host", "0.0.0.0", "--port", "8004"]
