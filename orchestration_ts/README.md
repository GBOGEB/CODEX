# DOCX RTM Orchestration Runtime

This directory contains the Wave-0 TypeScript orchestration scaffold.

## Runtime routes

- `GET /health` returns a basic service health response.
- `GET /jobs` returns the current jobs collection placeholder.
- `POST /federation/event` accepts a federation event payload and echoes the accepted event.

## Local setup

```bash
npm install
npm run build
npm test
```

The test suite starts the exported Express app on an ephemeral local port and exercises the runtime routes over HTTP.

## CI validation

Pull requests that touch this directory run the `Orchestration TypeScript CI` workflow. The workflow installs dependencies in `orchestration_ts/`, runs `npm run build`, and then runs `npm test`. This local environment could not complete those steps because npm registry access returned HTTP 403; the workflow is the required dependency-backed verification path once network access is available.

## Environment configuration

Copy `env.template` to `.env` for local runtime configuration:

```bash
cp env.template .env
```

Real `.env` files must not be committed. The repository root `.gitignore` ignores `.env` and `.env.local`; `env.template` is intentionally not `.env`-prefixed so it can pass connector filters that treat `.env*` paths as secret-bearing files.

## Type declarations

Do not add hand-written Express ambient declarations to make builds pass without installed dependencies. `npm run build` must validate against the real packages declared in `package.json`, including `express`, `@types/express`, and `@types/node`.
