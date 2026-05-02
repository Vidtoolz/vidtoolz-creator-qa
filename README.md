# Vidtoolz Creator QA

Vidtoolz Creator QA is a local Python CLI for checking VIDTOOLZ YouTube packaging and scripts before publishing.

v0.1 answers one question:

> Run packaging gate on this title/thumbnail/script and tell me what fails.

It parses a Markdown package with sections like `# Title`, `# Thumbnail`, `# Hook`, `# Script`, and `# Notes`, then runs deterministic checks for packaging clarity, promise alignment, viewer payoff, script structure, factual-claim risk, and DaVinci Resolve terminology.

## What It Does

- Scores each category from 0-5.
- Produces an overall gate result: `PASS`, `NEEDS WORK`, or `FAIL`.
- Prints a readable terminal summary.
- Can emit JSON for automation.
- Can write a Markdown report.
- Flags risky claims that need source notes or manual verification.
- Flags suspicious Resolve terms using an editable local lexicon in `data/resolve_terms.json`.

## What It Does Not Do

- No external APIs.
- No web calls.
- No LLM calls.
- No GUI.
- No database.
- It does not verify whether factual claims are true. It only detects claims that should be sourced manually.

## Install

From the repo root:

```bash
python -m pip install -e .
```

For one-off local runs without installing:

```bash
PYTHONPATH=src python -m creator_qa.cli check examples/resolve-tutorial-sample.md
```

## Usage

```bash
creator-qa check INPUT.md
creator-qa check INPUT.md --json
creator-qa check INPUT.md --report report.md
```

Example:

```bash
creator-qa check examples/resolve-tutorial-sample.md
```

## Sample Report

```text
Vidtoolz Creator QA Packaging Gate
Overall: PASS
Score: 29/30

Category scores:
- YouTube title clarity: 5/5
- Thumbnail / title promise alignment: 5/5
- Viewer payoff: 5/5
- Script structure: 5/5
- Factual-claim risk: 4/5
- Resolve terminology accuracy: 5/5

Warnings:
- Risky factual claims detected; source notes are present.

Risky factual claims needing source / manual verification:
- Resolve version and color-management behavior should be checked manually before publishing.

Top 3 fixes:
1. Review warning in Factual-claim risk.
```

Exact scores may change as local rules are edited.

## Markdown Input Format

```markdown
# Title
Fix Flat DaVinci Resolve Exports with Color Management

# Thumbnail
Fix Flat Exports

# Hook
By the end, you will know what settings to inspect.

# Script
## Hook
...

## Problem / Context
...

# Notes
Sources / manual verification:
- Resolve version should be checked manually before publishing.
```

Templates are available in `templates/`.

## Verification

Run:

```bash
./scripts/verify.sh
```

The script runs Python syntax checks, unit tests, and CLI smoke tests against the example package.

## Future Hermes Tool / Skill Path

This can become a Hermes tool or skill by keeping the deterministic checker as the core execution layer and wrapping it with a Hermes-facing interface that passes Markdown input and reads JSON output. The current `--json` output is intended to be stable enough for a future wrapper to consume, while Markdown reports remain readable for humans.
