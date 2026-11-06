# ---- Stage 1: install dependencies (build tools stay in this stage) ----
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: small runtime image ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /srv
COPY --from=builder /install /usr/local
COPY app ./app

# Run as a normal user, not root (least privilege)
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Set by CI to the git commit SHA, shown at /health
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
