# ==========================================
# Stage 1: Build & Dependency Resolution
# ==========================================
FROM python:3.12-slim AS builder

# Install Astral uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Cache dependency installations
COPY pyproject.toml uv.lock README.md /app/

# Synchronize dependencies into a standalone virtualenv
RUN uv sync --frozen --no-dev --no-install-project

# Copy project source code
COPY src /app/src
COPY app.py /app/app.py

# Install project package into the virtualenv
RUN uv sync --frozen --no-dev

# ==========================================
# Stage 2: Minimal Distroless/Slim Runtime
# ==========================================
FROM python:3.12-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    LEADPULSE_AUDIT_LOG_PATH="/app/data/audit.jsonl"

WORKDIR /app

# Create unprivileged application user & persistent data directory
RUN groupadd -r -g 1000 leadpulse && \
    useradd -r -u 1000 -g leadpulse -d /app leadpulse && \
    mkdir -p /app/data && \
    chown -R leadpulse:leadpulse /app

# Copy isolated virtual environment and application code from builder
COPY --from=builder --chown=leadpulse:leadpulse /app/.venv /app/.venv
COPY --from=builder --chown=leadpulse:leadpulse /app/src /app/src
COPY --from=builder --chown=leadpulse:leadpulse /app/app.py /app/app.py

USER leadpulse

EXPOSE 8000 8501

# Default entrypoint runs the FastAPI webhook gateway
CMD ["uvicorn", "leadpulse.api:app", "--host", "0.0.0.0", "--port", "8000"]
