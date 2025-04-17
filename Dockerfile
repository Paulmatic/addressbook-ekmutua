# Build stage
FROM python:3.9-slim as builder

WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    postgresql-client \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install wait-for-it
RUN curl -sSL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
    chmod +x /usr/local/bin/wait-for-it

# Create and configure non-root user
RUN useradd -m -u 1000 myuser && \
    mkdir -p /code/static /code/staticfiles /code/media /code/logs && \
    chown -R myuser:myuser /code && \
    chmod -R 755 /code/logs

# Copy Python dependencies from builder
COPY --from=builder --chown=myuser:myuser /code/wheels /wheels
COPY --from=builder --chown=myuser:myuser /code/requirements.txt .

# Install Python dependencies with cache cleanup
RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels && \
    pip cache purge

# Copy project files with correct permissions
COPY --chown=myuser:myuser . /code/

# Copy templates and static files
COPY --chown=myuser:myuser ./contacts/templates/ /code/contacts/templates/
COPY --chown=myuser:myuser ./contacts/static/ /code/contacts/static/

# Set directory permissions
RUN chmod -R 755 /code/static /code/staticfiles /code/media && \
    chmod +x /code/entrypoint.sh

# Configure environment variables
ENV PYTHONPATH=/code \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=addressbook.settings \
    PATH="/home/myuser/.local/bin:${PATH}"

# Health check with increased timeout
HEALTHCHECK --interval=30s --timeout=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Entrypoint script
USER myuser
ENTRYPOINT ["/code/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "addressbook.wsgi:application"]