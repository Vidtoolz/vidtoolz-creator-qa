# Failure Examples

The files in `examples/failures/` are intentionally weak packages. They prove Creator QA catches bad packages, not only polished samples.

Run one with:

```bash
creator-qa check examples/failures/bad-title-sample.md --profile resolve_tutorial
```

## Fixtures

- `bad-title-sample.md`: vague, generic title. Expected finding includes `title.vague`.
- `thumbnail-mismatch-sample.md`: title and thumbnail promise different outcomes. Expected finding includes `thumbnail.promise_mismatch`.
- `missing-viewer-payoff-sample.md`: package talks about the creator workflow without saying what the viewer gets. Expected finding includes `payoff.missing`.
- `weak-script-structure-sample.md`: script is too thin and misses required beats. Expected findings include `script.too_thin` and structure findings.
- `resolve-risky-claims-sample.md`: absolute/version/performance claims have no source notes. Expected finding includes `factual.risky_claim`.
- `suspicious-resolve-terms-sample.md`: uses suspicious Resolve terms such as render page and color tab. Expected finding includes `resolve.suspicious_term`.

These examples are part of the test suite and should remain weak. Do not improve them into passing examples unless the corresponding tests are updated with a new failure fixture.
