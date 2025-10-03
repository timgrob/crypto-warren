# -------- BUILDER STAGE --------
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install the UV CLI
RUN curl -sSL https://astral.sh/uv/install.sh | bash

# Setup the UV environment path correctly
ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync


# -------- RUNTIME STAGE --------
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY src/ src/
COPY main.py .

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV PYTHONPATH="/app/src"

# Expose the port
EXPOSE 8000

# Create non-root user and drop privileges
RUN adduser --system --group bot-user \
    && chown -R bot-user:bot-user /app
USER bot-user

# Run the Python file
CMD ["python", "main.py"]