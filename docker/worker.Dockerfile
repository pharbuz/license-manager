ARG PYTHON_VERSION=3.13.11-slim
FROM nexus-dh.yc.loc/python:${PYTHON_VERSION}

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates build-essential curl libpq-dev \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libharfbuzz0b libfribidi0 \
    libffi8 libxml2 libxslt1.1 \
    fonts-dejavu-core shared-mime-info \
    procps net-tools \
    && rm -rf /var/lib/apt/lists/*

COPY repo_conf/nexus.crt /usr/local/share/ca-certificates/nexus.crt
RUN chmod 0644 /usr/local/share/ca-certificates/nexus.crt && update-ca-certificates

COPY repo_conf/pip.conf /etc/pip.conf

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

RUN useradd -m -u 1000 appuser
RUN install -d -o appuser -g appuser /app /app/logs
WORKDIR /app
COPY --chown=appuser:appuser . .

USER appuser

RUN pip install --upgrade pip && \
    pip install --no-cache-dir .

# Keep runtime image lean: remove build/dev-only files from /app.
RUN rm -rf /app/tests \
    /app/README.md \
    /app/pyproject.toml \
    /app/Makefile \
    /app/.pre-commit-config.yaml \
    /app/.editorconfig \
    /app/.dockerignore \
    /app/run-Build_Docker_images*.sh

RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Default command (can be overridden by docker-compose)
CMD ["bash", "-lc", "celery -A app.license_manager.tasks.celery_app.celery_app worker -l info"]
