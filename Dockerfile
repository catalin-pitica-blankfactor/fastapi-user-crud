FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    if [ -s /app/requirements.txt ]; then pip install --no-cache-dir -r /app/requirements.txt; fi

copy . /app/

VOLUME ["/app", "/app/data"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]