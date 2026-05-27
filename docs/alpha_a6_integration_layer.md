# Alpha A6 MCP Sweep → GitHub Integration Layer (Concrete Spec)

## Scope
Defines the exact runtime seam between the local MCP Sweep Engine and GitHub API for crawling closed PR diffs, extracting near-miss candidates, and writing local telemetry/RTM deltas.

## Integration Contract
- **Input sources**: closed/merged PR metadata, review comments, commit messages, and aborted local session logs.
- **Output artifacts**:
  - `telemetry/mcp_sweep_YYYYMMDD.md`
  - `docs/rtm/delta/rtm_delta_YYYYMMDD.md`
  - optional `state/mcp_cursor.json` for incremental crawling.

## Authentication and Token Boundary Rules
- GitHub calls must use only `GITHUB_API_TOKEN` scoped minimally to read PRs/issues in target repos.
- No Office 365 or OneDrive credential can be loaded into this process.
- Token loading precedence: environment variable → local secret store lookup → fail-closed.

## API Endpoints (v3 REST)
1. `GET /repos/{owner}/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=50`
2. `GET /repos/{owner}/{repo}/pulls/{pull_number}/files`
3. `GET /repos/{owner}/{repo}/issues/{pull_number}/comments`
4. `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews`

## Near-Miss Heuristics
A candidate is marked **near-miss** when all apply:
1. PR is closed or merged in lookback window.
2. Diff/review text includes intent markers (`todo`, `follow-up`, `defer`, `future`, `out of scope`).
3. Candidate is not already present in local RTM delta index.
4. Candidate confidence score ≥ configured threshold (default `0.65`).

## Processing Loop
1. Load cursor and config from `_config/governance.yml`.
2. For each target repository, fetch closed PR pages until cursor stop.
3. Hydrate each PR with changed files and comments/reviews.
4. Extract near-miss candidates and deduplicate by normalized text hash.
5. Emit telemetry markdown and RTM delta rows.
6. Persist cursor (`updated_at`, `last_pr_number`) atomically.

## Failure Modes
- **Rate limited**: backoff with jitter; continue from saved cursor.
- **Invalid token**: fail-closed and emit security boundary violation log.
- **Schema mismatch**: quarantine record in telemetry under `PARSE-ERROR`.

## Minimal Python Module Layout
- `tools/mcp_sweep/github_client.py`
- `tools/mcp_sweep/extractors.py`
- `tools/mcp_sweep/rtm_writer.py`
- `tools/mcp_sweep/main.py`

## Definition of Done
- Dry-run mode produces deterministic markdown output from fixture PR payloads.
- Live mode can crawl at least one closed PR in `GBOGEB/CODEX` and emit one telemetry file.
- No corporate identity/token material is ever accessed by the sweep runtime.
