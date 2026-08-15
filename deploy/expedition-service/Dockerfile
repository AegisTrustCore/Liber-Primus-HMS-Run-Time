FROM python:3.12.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

LABEL org.opencontainers.image.title="HMS Expedition Sealed Verification Service" \
      org.opencontainers.image.version="0.3.0" \
      org.opencontainers.image.source="https://github.com/AegisTrustCore/Liber-Primus-HMS-Run-Time"

COPY requirements-runtime.txt requirements-service.txt /app/
RUN pip install --no-cache-dir --requirement /app/requirements-service.txt

COPY hms_tools /app/hms_tools
COPY scripts/serve_expedition_verifier.py /app/scripts/serve_expedition_verifier.py
COPY deploy/expedition-service/gunicorn.conf.py /app/gunicorn.conf.py
COPY deploy/expedition-service/openapi.yaml /app/openapi.yaml

USER 65532:65532
EXPOSE 8080

CMD ["gunicorn", "--config", "/app/gunicorn.conf.py", "scripts.serve_expedition_verifier:create_application_from_environment()"]
