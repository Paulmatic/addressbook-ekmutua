# Build stage
FROM python:3.9-slim as builder

WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /code

# Install system dependencies including curl and PostgreSQL client first
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install wait-for-it properly
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
    chmod +x /usr/local/bin/wait-for-it

# Create non-root user and directories
RUN useradd -m myuser && \
    mkdir -p /code/static /code/staticfiles /code/media && \
    chown -R myuser:myuser /code

# Copy Python dependencies from builder
COPY --from=builder --chown=myuser:myuser /code/wheels /wheels
COPY --from=builder --chown=myuser:myuser /code/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels

# Copy project files with correct permissions
COPY --chown=myuser:myuser . /code/

# Set directory permissions
RUN chmod -R 755 /code/static /code/staticfiles /code/media

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Entrypoint script
COPY --chown=myuser:myuser entrypoint.sh /code/
RUN chmod 755 /code/entrypoint.sh

USER myuser

ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "addressbook.wsgi:application"]