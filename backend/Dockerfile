FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000

# install curl for running healthcheck in docker-compose
RUN apt update && \
    apt full-upgrade -y && \
    apt install curl -y

# Create app user
RUN groupadd -g $GID appgroup && \
    useradd -m -u $UID -g appgroup appuser

FROM base AS builder
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml ./uv.lock ./

# install minimum required
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

FROM base AS dev
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml ./uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

RUN chown -R appuser:appgroup /app

USER appuser

CMD ["fastapi", "dev", "app/main.py", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS prod
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv/

COPY ./app /app/app

ENV PATH="/app/.venv/bin:$PATH"

RUN chown -R appuser:appgroup /app

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]