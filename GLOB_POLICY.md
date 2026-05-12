# Glob Policy

## Purpose

This policy defines which files are source, generated, published, archived, or forbidden. It prevents stale outputs, duplicate dashboard variants, broken Pages links, and local-folder drift.

## Source files

Allowed source globs:

```text
README.md
LICENSE
NOTICE.md
TOOL_INDEX.md
VERSION.json
MANIFEST.json
BACKBONE_POLICY.md
.github/workflows/*.yml
schema/*.json
scripts/*.py
tests/*.py
tools/*/README.md
tools/*/VERSION.json
tools/*/MANIFEST.json
tools/*/src/**/*.py
tools/*/data/**/*.json
tools/*/data/**/*.csv
tools/*/assets/**/*
tools/*/tests/**/*.py
```

## Published GitHub Pages files

Allowed published globs:

```text
docs/index.html
docs/dashboard.html
docs/handover.html
docs/verification.html
docs/regression.html
docs/traceability.html
docs/manifest.html
docs/plots/index.html
docs/plots/*.html
docs/assets/**/*
```

## Local generated files

Allowed local generated globs:

```text
tools/*/outputs/**/*
tools/*/reports/**/*
```

These may be committed only if explicitly required for traceability or release evidence.

## Release snapshots

Allowed release globs:

```text
releases/**/MANIFEST.json
releases/**/README.md
releases/**/*.html
releases/**/*.pdf
releases/**/*.json
```

Release snapshots are immutable once tagged.

## Archive files

Allowed archive globs:

```text
archive/retired_artifacts/**/*
```

Archived files must not be linked as canonical live outputs.

## Forbidden ambiguity globs

The following patterns are forbidden unless explicitly justified in a migration note:

```text
**/final/**
**/final_final/**
**/latest/**
**/new_dashboard/**
**/dashboard_old/**
**/dashboard_new/**
**/copy*/**
**/*backup*/**
**/*_old.*
**/*_new.*
**/*_final.*
**/*_latest.*
```

## Required checks

Every PR must verify:

```text
no forbidden ambiguity globs
no duplicate canonical dashboard files
no orphan published HTML files
no broken relative links
no stale plot files
no missing manifest entries
no untracked public entrypoints
```
