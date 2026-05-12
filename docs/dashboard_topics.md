# Core Topic EP Dashboard blueprint

## GitHub Pages setup
1. Keep dashboard artifacts in `/docs`.
2. In repository settings, set Pages source to `main` branch `/docs` folder.
3. Publish `dashboard.html` as entry page, optionally rename to `index.html`.

## Backbone architecture
- **Python layer**: aggregates markdown, YAML slide specs, and test status into a `topics.json` file.
- **JavaScript layer**: reads the JSON and provides filtering, search, and rendered previews.
- **Rendered output**: both markdown and HTML views supported for engineering handover.

## Recommended naming
- Core Topic EP Dashboard
- Themed Topics & Epics Portal
- Engineering Program Epic Hub


## Pending review + parallel track
Use a dual-PR model: merge a minimal baseline branch, while a parallel `review/followups-*` branch collects all comment-driven updates before final approval. See `docs/review_parallel_track.md`.
