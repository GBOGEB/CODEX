FROM node:22-bookworm-slim AS node_runtime

FROM python:3.11-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# validate_all.py executes npx/tsx when the TypeScript federation tests are
# present. Copy a pinned Node major from the official Node image so the
# canonical container exercises the same mixed Python/TypeScript validator.
COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node_runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

COPY requirements.txt pyproject.toml package.json ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && npm install --no-audit --no-fund

COPY . .
RUN python -m pip install --no-cache-dir -e .

RUN useradd --create-home codex \
    && chown -R codex:codex /workspace
USER codex

CMD ["python", "scripts/validate_all.py"]
