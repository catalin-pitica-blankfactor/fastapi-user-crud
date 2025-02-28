FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements-tests.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir -r /app/requirements-tests.txt && \
    pip install --no-cache-dir mypy isort black flake8 pylint coverage


copy . /app/

VOLUME ["/app", "/app/data"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]