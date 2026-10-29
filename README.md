# kwintent

Intent-based keyword research for SEO and GEO. No third-party SEO data: an LLM, called through
[OpenRouter](https://openrouter.ai), estimates everything.

```bash
pip install -e .[dev]
export OPENROUTER_API_KEY=...        # optional: OPENROUTER_MODEL=<slug>, default openrouter/auto
kwintent serve                        # web UI at http://127.0.0.1:8000
kwintent research --business "Project management app for small construction firms" --out out/
kwintent research --business "x" --demo   # canned sample data, no API call
```

Pipeline: business profile -> intent map (jobs people are trying to get done) -> per-intent
SEO keywords and GEO prompts (questions asked to AI assistants) -> estimated volume band,
difficulty, AI-answer risk, business value -> deterministic opportunity score
(`kwintent/scoring.py`).

![UI](docs/ui-seo.png)
(The screenshot uses `--demo` sample data, not real estimates.)

## Limits
Estimates are LLM guesses in coarse bands, not measurements; use them to rank and to pick what
to validate. GEO "demand" has no public ground truth at all. Output quality depends on the
model you choose; `openrouter/auto` picks one for you, so results may vary between runs.
