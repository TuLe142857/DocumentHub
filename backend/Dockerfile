# --------------------------------------------------
#           TARGET: base
# --------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000

# install curl for running healthcheck in docker-compose
RUN apt update && \
    apt upgrade -y && \
    apt install curl -y
# Create app user
RUN groupadd -g $GID appgroup && \
    useradd -m -u $UID -g appgroup appuser


# --------------------------------------------------
#           TARGET: builder
# - Install minimum dependencies
# --------------------------------------------------
FROM base AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml ./uv.lock ./
COPY ./backend/pyproject.toml /app/backend/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-install-workspace --no-dev


# --------------------------------------------------
#           TARGET: dev
# - Use local development
# - Source code must be mount in docker-compose for 
# hot reload
# - Copy from builder and install full dependencies 
# (include dev dependencies)
# --------------------------------------------------
FROM base AS dev

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml ./uv.lock ./
COPY ./backend/pyproject.toml /app/backend/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-install-workspace
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/backend
RUN chown -R appuser:appgroup /app
USER appuser

CMD ["fastapi", "dev", "app/main.py", "--reload", "--host", "0.0.0.0", "--port", "8000"]


# --------------------------------------------------
#           TARGET: prod
# - Optimize for final production image
# --------------------------------------------------
FROM base AS prod

WORKDIR /app
COPY backend/app /app/backend/app
COPY --from=builder /app/.venv /app/.venv/
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/backend
RUN chown -R appuser:appgroup /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]