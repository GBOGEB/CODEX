# Reproducible Software Build and GitHub-Tracked Development Process

## Executive summary

This report treats “project kickoff through the first production-ready release and operational handoff” as the path from initial repository bootstrap through the first production-ready release and operational handoff. For a GitHub-centered delivery model, the strongest default is a protected-trunk workflow: short-lived working branches, pull requests as the unit of review and audit, GitHub Issues/Projects/Milestones as the work system, and GitHub Actions as the automation plane.

For reproducibility, the central design principle is to make the repository the single operational contract for both humans and automation: pin the runtime/toolchain, commit the correct lockfiles or wrappers for the chosen ecosystem, document the exact install and validation commands used by CI, and have local development call those same commands.

For release management, the cleanest generic model is SemVer for version numbers, Conventional Commits for commit intent, signed release tags, GitHub Releases for distributable artifacts, and GitHub’s automated release notes with a repository-level `.github/release.yml` so changelog categories stay consistent over time.

## Operating model from kickoff to first release

A robust GitHub operating model starts by separating three concerns that are often mixed together: product intent, tracked work, and delivery automation.

- **Product intent** belongs in README, docs, and ADRs.
- **Tracked work** belongs in GitHub Issues, Projects, and Milestones.
- **Delivery automation** belongs in `.github/workflows`, scripts, and reproducible build commands.

Recommended branch model:

- Protected `main`
- Short-lived topic branches
- Pull-request-only merge policy
- Required checks and reviews
- CODEOWNERS on sensitive paths

## Current repository landmarks

```text
repo/
├── .github/
│   └── workflows/
├── docs/
├── outputs/
├── scripts/
├── src/
├── tests/
├── README.md
├── pyproject.toml
├── requirements.txt
├── MANIFEST.json
└── GLOB_POLICY.md
```

This repository does not currently define a root `Makefile`, so the reproducibility contract should stay aligned with the Python commands already exercised by CI.

## Build reproducibility baseline

Use the repository's documented, CI-matching entrypoints as the contract:

- `python -m pip install -e '.[dev]'`
- `python -m pytest -q`
- `python scripts/check_manifest.py`
- `python scripts/check_globs.py`
- `python scripts/check_stale.py`
- `python scripts/check_links.py`

These commands match the repository's current validation flow. If the project later adds a stable wrapper such as a root `Makefile`, update both this document and CI together so the documented command surface remains true.

## Security and release controls

Recommended minimum controls:

- Dependabot for dependency + Action updates
- Dependency review on PRs
- Code scanning (CodeQL or equivalent)
- Least-privilege workflow permissions
- Secret scanning
- Artifact attestations and SBOM generation
- OIDC-based deployment auth (avoid long-lived cloud secrets)

Release model:

- Conventional Commits + SemVer
- Signed tags (`vMAJOR.MINOR.PATCH`)
- GitHub Release artifacts
- Automated, categorized release notes via `.github/release.yml`

## Initial four-week rollout (starting Monday, May 18, 2026)

1. **Week 1:** Repository governance baseline (docs, templates, rulesets, tracking setup)
2. **Week 2:** Build/test reproducibility contract and CI integration
3. **Week 3:** Security gates and release pipeline
4. **Week 4:** Environment promotion flow (`dev` → `stage` → `prod`) and handoff docs

## Exit criterion

A new engineer can clone the repo, install the documented development dependencies, open an issue-linked branch, pass CI via PR, merge into protected `main`, cut a signed release tag, and promote the same release artifact across environments using only documented runbooks.
