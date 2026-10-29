import csv
import json
from pathlib import Path

DISCLAIMER = (
    "> **All volume, difficulty and demand figures are Claude's estimates from general "
    "knowledge. No search, SERP or AI-citation data was used. Treat them as coarse bands "
    "good for relative ranking, not forecasts. Validate the top picks against Google "
    "Search Console, a real SERP check, or by prompting AI assistants yourself.**\n")


def _csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write(result: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(result, indent=2))
    _csv(out / "keywords.csv", result["seo_keywords"])
    _csv(out / "geo_prompts.csv", result["geo_prompts"])

    md = ["# Intent-based keyword research\n", DISCLAIMER,
          f"**Business:** {result['business']['description']}\n",
          "## Intents\n", "| Intent | Type | Stage | Fit | Problem |", "|---|---|---|---|---|"]
    for i in result["intents"]:
        md.append(f"| {i['name']} | {i['intent_type']} | {i['journey_stage']} | "
                  f"{i['business_fit']}/5 | {i['searcher_problem']} |")
    md += ["\n## Top SEO keywords (by opportunity score)\n",
           "| Keyword | Intent | Est. volume | Conf. | Difficulty | AI risk | Score |",
           "|---|---|---|---|---|---|---|"]
    for k in result["seo_keywords"][:30]:
        md.append(f"| {k['keyword']} | {k['intent_id']} | {k['volume_band']} | "
                  f"{k['volume_confidence']} | {k['difficulty']} | {k['ai_overview_risk']} "
                  f"| {k['score']} |")
    md += ["\n## Top GEO prompts (by opportunity score)\n",
           "| Prompt | Intent | Demand | Citation difficulty | Format | Score |",
           "|---|---|---|---|---|---|"]
    for g in result["geo_prompts"][:30]:
        md.append(f"| {g['prompt']} | {g['intent_id']} | {g['demand']} | "
                  f"{g['citation_difficulty']} | {g['content_format']} | {g['score']} |")
    (out / "report.md").write_text("\n".join(md) + "\n")
