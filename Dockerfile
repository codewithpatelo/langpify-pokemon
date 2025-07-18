FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD [ "sh", "-c", "\
  if [ \"$ENVIRONMENT\" = 'DEVELOPMENT' ]; then \
    echo 'Running Uvicorn in development mode...' && \
    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload; \
  else \
    echo 'Running Gunicorn in production mode...' && \
    gunicorn app.main:app -c gunicorn_conf.py; \
  fi" ]

