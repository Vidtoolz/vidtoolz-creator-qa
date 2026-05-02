# Creator QA Profiles

Profiles tune the deterministic gate for different creator package types. They do not call external APIs and do not change the Markdown parser.

Use a profile with:

```bash
creator-qa check INPUT.md --profile resolve_tutorial
```

If `--profile` is omitted, Creator QA uses `resolve_tutorial`.

## Supported Profiles

- `resolve_tutorial`: strict long-form DaVinci Resolve tutorial checks. Requires title, thumbnail, hook, and script. Uses strict factual-risk detection and strict Resolve terminology checks.
- `shorts`: short-form video checks. Thumbnail is optional, title and thumbnail tolerances are tighter, and the expected script structure is shorter.
- `ai_video_breakdown`: AI workflow analysis checks. Requires notes because model, tool, date, pricing, and capability claims are likely to need manual verification.
- `kit_newsletter`: newsletter package checks. Thumbnail is optional and the title tolerance is longer.
- `product_affiliate_page`: product recommendation checks. Requires notes because price, feature, compatibility, and affiliate claims need manual verification.

## What Profiles Tune

- Expected sections.
- Title length tolerance.
- Thumbnail text tolerance.
- Whether thumbnail text is required.
- Required script beats.
- Minimum useful script length.
- Factual-risk sensitivity.
- Whether suspicious Resolve terminology is ignored, warned, or failed.

## Gate Meaning

- `PASS`: no fail-severity findings and the score is strong enough for the selected profile.
- `NEEDS WORK`: warnings, non-critical fail findings, partial structure problems, or a score below the pass threshold exist.
- `FAIL`: a critical publishing problem exists.

Critical publishing problems include missing title, missing viewer payoff, no usable script, title/thumbnail promise conflict, strict Resolve terminology suspicion in a Resolve tutorial, and risky factual claims without source notes.
