# FinanceRAG Celery worker image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY app ./app
RUN pip install --no-cache-dir --timeout 120 --retries 10 .

RUN useradd --create-home --uid 1000 financerag \
    && mkdir -p /data/documents \
    && chown -R financerag:financerag /data/documents
USER financerag

CMD ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=INFO", "--concurrency=2"]