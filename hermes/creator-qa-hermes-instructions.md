# Hermes Instructions: Creator QA

Run Creator QA when a user asks to prepare, review, approve, publish, or hand off a VIDTOOLZ creator package, especially YouTube title/thumbnail/script work and DaVinci Resolve tutorials.

Use a Markdown package file with top-level sections such as:

- `# Title`
- `# Thumbnail`
- `# Hook`
- `# Viewer Payoff`
- `# Script`
- `# Factual Claims Needing Source`
- `# Resolve Terminology Used`
- `# Notes`

Default command:

```bash
./scripts/hermes-creator-qa.sh INPUT.md
```

Use `--json` when Hermes needs machine-readable fields. Use `--profile` when the content type is known.

Interpret results strictly:

- `PASS`: no fail-severity findings and a strong score for the selected profile.
- `NEEDS WORK`: the package has warnings, partial structure problems, non-critical failures, or a weak score.
- `FAIL`: publishing blocker. Do not recommend publishing until fixed.

When reporting to the user:

- State the overall result.
- Summarize the top 3 fixes.
- List risky factual claims and suspicious Resolve terms when present.
- Treat risky claims as needing source notes or manual verification, not as verified truth.
- Do not override Creator QA results with vague encouragement.
- Ask the user to rerun Creator QA after fixes.
