# kwintent

Intent-based keyword research for SEO and GEO. No third-party data: Claude estimates everything.

```bash
pip install -e .[dev]
export ANTHROPIC_API_KEY=...
kwintent research --business "Project management app for small construction firms" \
  --audience "site managers, owners" --site-strength new --out out/
```

Pipeline: business profile -> intent map (jobs people are trying to get done) -> per-intent
SEO keywords and GEO prompts (questions asked to AI assistants) -> estimated volume band,
difficulty, AI-overview risk, business value -> deterministic opportunity score
(`kwintent/scoring.py`). Outputs `report.md`, `keywords.csv`, `geo_prompts.csv`, `results.json`.

## Limits
Estimates are LLM guesses in coarse bands, not measurements; use them to rank and to pick
what to validate, not to forecast traffic. GEO "demand" has no public ground truth at all.
Model defaults to `claude-opus-5-5`; override with `--model` or `KWINTENT_MODEL`.
