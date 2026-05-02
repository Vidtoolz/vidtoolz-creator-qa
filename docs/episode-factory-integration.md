# Episode Factory Integration

Vidtoolz Episode Factory can integrate with Creator QA by exporting creator packages into either Markdown or JSON.

## Markdown Export Path

The simplest integration is for Episode Factory to write a Markdown package with Creator QA sections:

```markdown
# Title
...

# Thumbnail
...

# Hook
...

# Script
...

# Notes
Sources / manual verification:
- ...
```

Then run:

```bash
creator-qa check episode.md --json
creator-qa check episode.md --hermes-report
creator-qa check episode.md --linear-report
```

This keeps Episode Factory responsible for drafting and packaging, while Creator QA remains the deterministic gate.

## JSON Export Path

A later Episode Factory export can map its internal package model into Creator QA's stable JSON output fields:

- `overall_result`
- `total_score`
- `max_score`
- `category_scores`
- `findings`
- `warnings`
- `risky_claims`
- `suspicious_terms`
- `top_fixes`
- `input_sections_detected`
- `created_at`

For ingestion, Episode Factory should treat finding `id` values as stable rule identifiers and avoid depending on exact human wording in `message`.

## Recommended Flow

1. Episode Factory exports a Markdown package.
2. Creator QA runs deterministic checks locally.
3. Hermes reads `--hermes-report` for memory-friendly summary.
4. Linear receives `--linear-report` when failed checks need tracking.
5. Episode Factory stores `--json` output as machine-readable QA evidence.

Creator QA does not verify factual truth. It flags risky claims that need sources or manual verification before publishing.
