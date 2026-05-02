# Hermes Integration

Creator QA v0.4 adds a local Hermes adapter layer without requiring Hermes internals to change.

## Wrapper Command

Hermes can call:

```bash
./scripts/hermes-creator-qa.sh INPUT.md
```

The wrapper activates `.venv` when available, defaults to `--hermes-report`, and defaults to `--profile resolve_tutorial`. It never modifies the checked Markdown file.

Examples:

```bash
./scripts/hermes-creator-qa.sh examples/resolve-tutorial-sample.md
./scripts/hermes-creator-qa.sh examples/failures/bad-title-sample.md --profile resolve_tutorial
./scripts/hermes-creator-qa.sh examples/failures/thumbnail-mismatch-sample.md --json
```

## Hermes Usage

Hermes should create or receive a Markdown package, run the wrapper, and summarize the result. `FAIL` is a publishing blocker. `NEEDS WORK` means the package should be revised before handoff. `PASS` means the deterministic gate found no fail-severity issues and the score is strong enough for the selected profile.

Hermes should report the top 3 fixes and ask the user to rerun Creator QA after edits. Hermes should not soften a `FAIL` or replace the deterministic result with general encouragement.

## Codex Usage

Codex should run Creator QA before publishing-related commits when the change affects creator packaging, scripts, Resolve tutorial copy, example reports, or adapter behavior.

Use:

```bash
./scripts/hermes-creator-qa.sh path/to/package.md
```

For automation checks, use:

```bash
./scripts/hermes-creator-qa.sh path/to/package.md --json
```

When Hermes receives an Episode Factory JSON export, call Creator QA directly:

```bash
creator-qa check-episode-json path/to/episode.json --hermes-report
```

## Episode Factory Path

Episode Factory can export an episode package into `templates/creator-qa-package.md` shape, write it as Markdown, and pass that file to the wrapper. It can also export JSON and pass that file to `creator-qa check-episode-json`. JSON output can be stored as QA evidence, while the Hermes report can be pasted into memory or review notes.

## Manual in v0.4

- Confirm factual claims using source notes or manual verification.
- Decide whether a weak but intentional creative choice is acceptable.
- Select the correct profile when the package is not a Resolve tutorial.
- Move results into Hermes memory, Linear, or Episode Factory storage.
- Rerun QA after package edits.
