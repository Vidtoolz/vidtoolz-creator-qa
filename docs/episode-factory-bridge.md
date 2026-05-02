# Episode Factory Bridge

Creator QA v0.5 can read a Vidtoolz Episode Factory JSON export directly or render it into the standard Creator QA Markdown package format.

## Commands

Check an Episode Factory JSON export:

```bash
creator-qa check-episode-json examples/episode-factory/resolve-episode-good.json
```

Render the export to Markdown:

```bash
creator-qa render-package examples/episode-factory/resolve-episode-good.json --output /tmp/creator-qa-package.md
```

The adapter is tolerant of missing optional fields. Missing data may still produce Creator QA findings, but it should not crash the parser.

## Field Mapping

Episode Factory JSON fields map into Creator QA sections as follows:

- `title` -> `# Title`
- `thumbnailText` -> `# Thumbnail`
- `thumbnailConcept` -> `# Thumbnail` when `thumbnailText` is missing
- `hook` -> `# Hook`
- `viewerPayoff` -> `# Viewer Payoff`
- `promise` -> `# Viewer Payoff` when `viewerPayoff` is missing
- `scriptOutline` -> `# Script`
- `script` -> `# Script`
- `notes` -> `# Notes`
- `factualClaims` -> `# Notes` as claims needing source notes
- `sourceNotes` -> `# Notes` as source/manual verification notes
- `status` -> `# Notes`
- `packagingGate` -> `# Notes`
- `checklist` -> `# Notes`
- `shortsIdeas` -> `# Notes`
- `nextAction` -> `# Notes`

Objects and arrays are rendered into readable Markdown lines. Unknown fields are ignored in v0.5.

## Episode Factory Export Path

Episode Factory can export a JSON object using the fields above, save it locally, then call:

```bash
creator-qa check-episode-json path/to/episode.json --json
```

The JSON result can be stored as QA evidence. Markdown report modes can be used for human review, Hermes memory, or Linear comments.

## Hermes Usage

Hermes can use this bridge when it receives an Episode Factory JSON export instead of a Markdown package. For user-facing summaries, run:

```bash
creator-qa check-episode-json path/to/episode.json --hermes-report
```

Hermes should treat `FAIL` as a publishing blocker, summarize the top 3 fixes, and ask the user to rerun Creator QA after edits.

## Manual in v0.5

- Confirm factual claims with real source notes or manual verification.
- Choose the correct QA profile when the export is not a Resolve tutorial.
- Decide how Episode Factory stores the rendered Markdown and QA JSON evidence.
- Review unknown Episode Factory fields before adding new mappings.
