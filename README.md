# Vidtoolz Creator QA

Vidtoolz Creator QA is a local Python CLI for checking VIDTOOLZ YouTube packaging and scripts before publishing.

v0.3 answers one question:

> Run packaging gate on this title/thumbnail/script and tell me what fails.

It parses a Markdown package with sections like `# Title`, `# Thumbnail`, `# Hook`, `# Script`, and `# Notes`, then runs deterministic checks for packaging clarity, promise alignment, viewer payoff, script structure, factual-claim risk, and DaVinci Resolve terminology.

## What It Does

- Scores each category from 0-5.
- Produces an overall gate result: `PASS`, `NEEDS WORK`, or `FAIL`.
- Prints a readable terminal summary.
- Can emit JSON for automation.
- Can write a Markdown report.
- Can print compact Hermes and Linear Markdown reports.
- Emits stable rule IDs for machine-readable findings.
- Flags risky claims that need source notes or manual verification.
- Flags suspicious Resolve terms using an editable local lexicon in `data/resolve_terms.json`.
- Supports QA profiles for Resolve tutorials, Shorts, AI video breakdowns, Kit newsletters, and product affiliate pages.
- Includes intentionally weak fixtures to prove failure paths.

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
creator-qa check INPUT.md --profile resolve_tutorial
creator-qa check INPUT.md --json
creator-qa check INPUT.md --report report.md
creator-qa check INPUT.md --hermes-report
creator-qa check INPUT.md --linear-report
```

Normal terminal check:

```bash
creator-qa check examples/resolve-tutorial-sample.md
```

JSON output:

```bash
creator-qa check examples/resolve-tutorial-sample.md --json
```

Profile-specific check:

```bash
creator-qa check examples/resolve-tutorial-sample.md --profile resolve_tutorial
```

Markdown report output:

```bash
creator-qa check examples/resolve-tutorial-sample.md --report report.md
```

Hermes memory report output:

```bash
creator-qa check examples/resolve-tutorial-sample.md --hermes-report
```

Linear issue/comment output:

```bash
creator-qa check examples/resolve-tutorial-sample.md --linear-report
```

## Sample Report

```text
Vidtoolz Creator QA Packaging Gate
Overall: PASS
Profile: resolve_tutorial
Score: 35/35

Category scores:
- Expected package structure: 5/5
- YouTube title clarity: 5/5
- Thumbnail / title promise alignment: 5/5
- Viewer payoff: 5/5
- Script structure: 5/5
- Factual-claim risk: 5/5
- Resolve terminology accuracy: 5/5
```

Exact scores may change as local rules are edited.

Example outputs are available in `examples/reports/`.

## Profiles

If `--profile` is omitted, Creator QA uses `resolve_tutorial`.

Supported profiles:

- `resolve_tutorial`
- `shorts`
- `ai_video_breakdown`
- `kit_newsletter`
- `product_affiliate_page`

Profiles tune expected sections, title length tolerance, thumbnail text tolerance, required script beats, minimum script depth, factual-risk sensitivity, and terminology checking. See `docs/profiles.md`.

## Gate Results

- `PASS`: no fail-severity findings and a strong enough score for the selected profile.
- `NEEDS WORK`: warnings, non-critical fail findings, partial structure problems, or a score below the pass threshold exist.
- `FAIL`: a critical publishing problem exists.

Critical publishing problems include missing title, missing viewer payoff, no usable script, title/thumbnail promise conflict, major Resolve terminology suspicion in a Resolve tutorial, and risky factual claims with no source notes.

## Failure Examples

Intentionally weak fixtures live in `examples/failures/`:

- `bad-title-sample.md`
- `thumbnail-mismatch-sample.md`
- `missing-viewer-payoff-sample.md`
- `weak-script-structure-sample.md`
- `resolve-risky-claims-sample.md`
- `suspicious-resolve-terms-sample.md`

Run them when changing rules to confirm the gate is not overly flattering:

```bash
creator-qa check examples/failures/thumbnail-mismatch-sample.md --profile resolve_tutorial
```

See `docs/failure-examples.md`.

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

## Machine-Readable Output

`--json` includes:

- `overall_result`
- `profile`
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

Each finding includes `id`, `severity`, `category`, `message`, and `suggestion`. Treat finding IDs as stable automation keys.

## Hermes Tool / Skill Path

This can become a Hermes tool or skill by keeping the deterministic checker as the core execution layer and wrapping it with a Hermes-facing interface that passes Markdown input and reads JSON output. The current `--json` output is intended to be stable enough for a future wrapper to consume, while Markdown reports remain readable for humans.

Use `--hermes-report` when the result should be pasted into Hermes memory.

## Episode Factory Integration

Vidtoolz Episode Factory can later export Markdown packages into Creator QA, run `creator-qa check episode.md --json`, and store the result as QA evidence. For task tracking, it can route `--linear-report` into Linear. For memory, it can route `--hermes-report` into Hermes.

See `docs/episode-factory-integration.md` for the intended integration path.
