# FinanceRAG API image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the project (runtime dependencies only, no dev tools)
COPY pyproject.toml README.md LICENSE ./
COPY alembic.ini ./
COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts
RUN pip install --no-cache-dir .

# Run as an unprivileged user
RUN useradd --create-home --uid 1000 financerag \
    && mkdir -p /data/documents \
    && chown -R financerag:financerag /data/documents
USER financerag

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]