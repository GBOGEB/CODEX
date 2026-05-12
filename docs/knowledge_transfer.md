# Engineering App / Tool / Knowledge Transfer Program

## Purpose
This program turns repository artifacts into a repeatable engineering knowledge-transfer product delivered as:
- HTML slides for executive and onboarding walkthroughs.
- Rendered Markdown for detailed implementation and operating guidance.
- Integrated global entry points so users can discover the content from the main CODEX portal.

## Phase Plan

### Phase 0 — Discovery and Governance
- Confirm the audience (engineering, quality, operations, PMO).
- Define scope boundaries (tooling, architecture, operational handover, verification).
- Establish ownership, review cadence, and acceptance criteria.

### Phase 1 — Information Architecture
- Organize content into tracks:
  1. Engineering app/tool architecture
  2. Build and runtime workflows
  3. Quality and verification evidence
  4. Operational handover
- Map existing source documents and generated HTML outputs into these tracks.

### Phase 2 — Slide System (HTML)
- Build browser-native slides with sections for context, architecture, execution model, and adoption.
- Keep a short “leadership path” and a deeper “engineering path.”
- Version the slides alongside source documents.

### Phase 3 — Rendered Markdown Knowledge Base
- Maintain canonical Markdown pages for each phase deliverable.
- Publish rendered Markdown to `/docs` for GitHub Pages consumption.
- Add cross-links from slides into deeper rendered docs.

### Phase 4 — Global Integration (GBOGEB/CODEX)
- Register links in the global portal (`docs/index.html`) so users discover the content from the root page.
- Add dashboard links and navigation consistency checks.
- Validate all links with repository checks.

### Phase 5 — Operationalization
- Add a release checklist (content freeze, QA pass, publish, announce).
- Track version history and change log for knowledge-transfer assets.
- Schedule quarterly refreshes and post-mortem updates.

## Execution Checklist
- [ ] Audience and owners confirmed
- [ ] Content tracks approved
- [ ] Slides reviewed by engineering lead
- [ ] Rendered Markdown reviewed by quality lead
- [ ] Global portal links validated
- [ ] First release published

## Success Criteria
- New engineer can navigate from the global CODEX portal to:
  1. high-level slides in < 2 clicks,
  2. detailed procedural docs in < 3 clicks,
  3. verification evidence in < 4 clicks.
- All referenced pages are static, link-valid, and versioned in-repo.
