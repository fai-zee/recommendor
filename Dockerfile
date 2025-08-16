FROM python:3.11-slim
WORKDIR /code
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .[dev]
COPY . .
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
