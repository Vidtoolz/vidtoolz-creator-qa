# Agent Instructions

## Repo Purpose

This repository contains Vidtoolz Creator QA, a local Python CLI verifier for VIDTOOLZ YouTube packaging and scripts.

The v0.5 goal is to answer:

> Run packaging gate on this title/thumbnail/script and tell me what fails.

v0.3 must prove weak packages are caught, not only that good packages pass.
v0.4 adds a local Hermes/Codex adapter layer without modifying Hermes internals.
v0.5 adds an Episode Factory JSON bridge.

## Constraints

- Keep v0.1 local-only.
- Do not add web calls.
- Do not add LLM calls.
- Do not add external API calls.
- Do not add a GUI.
- Do not add a database.
- Prefer Python standard library unless a dependency is clearly necessary.
- Keep rules deterministic and easy to inspect.
- Keep output readable by Hermes and humans.
- Keep rule IDs stable once introduced.
- Do not remove JSON fields without documenting a migration path.
- Every new rule needs at least one good-path test and one failure-path test.
- Do not make the gate overly flattering.
- Creator QA should be stricter than a normal writing assistant.
- Adapter wrappers must stay local-only.
- Adapter wrappers must not mutate checked input files.
- Every adapter change must include a smoke test in `scripts/verify.sh`.
- Do not break existing Markdown input.
- Keep JSON adapters tolerant of missing optional fields.
- Every Episode Factory field mapping must be documented.
- Every new input shape needs tests.

## Verification

Always run:

```bash
./scripts/verify.sh
```

before handing off changes.

## Output Expectations

- Terminal output should be readable by a human.
- JSON output should be stable and machine-readable.
- Markdown reports should be clear enough to paste into creator workflows.
- Risky factual claims should be labeled as needing source notes or manual verification, not treated as verified truth.
