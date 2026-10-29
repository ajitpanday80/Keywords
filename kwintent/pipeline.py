from concurrent.futures import ThreadPoolExecutor

from . import prompts, scoring
from .llm import LLM
from .models import Business, IntentExpansion, IntentMap


def run(llm: LLM, biz: Business, n_intents: int = 10, n_seo: int = 12,
        n_geo: int = 8, workers: int = 4) -> dict:
    imap = llm.parse(prompts.SYSTEM, prompts.intent_map_prompt(biz, n_intents), IntentMap)
    intents = imap.intents

    def expand(intent):
        return llm.parse(prompts.SYSTEM,
                         prompts.expansion_prompt(biz, intent, n_seo, n_geo),
                         IntentExpansion)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        expansions = list(ex.map(expand, intents))

    seo, geo, seen_seo, seen_geo = [], [], set(), set()
    for intent, exp in zip(intents, expansions):
        for k in exp.seo_keywords:
            key = " ".join(k.keyword.lower().split())
            if key in seen_seo:  # same query under two intents: keep first, avoid cannibalization
                continue
            seen_seo.add(key)
            row = k.model_dump()
            row.update(intent_id=intent.id, intent_type=intent.intent_type,
                       est_volume=scoring.volume_midpoint(k.volume_band),
                       score=scoring.seo_score(k.volume_band, k.volume_confidence,
                                               k.difficulty, k.ai_overview_risk,
                                               k.business_value, intent.business_fit))
            seo.append(row)
        for g in exp.geo_prompts:
            key = " ".join(g.prompt.lower().split())
            if key in seen_geo:
                continue
            seen_geo.add(key)
            row = g.model_dump()
            row.update(intent_id=intent.id, intent_type=intent.intent_type,
                       score=scoring.geo_score(g.demand, g.citation_difficulty,
                                               g.business_value, intent.business_fit))
            geo.append(row)
    seo.sort(key=lambda r: -r["score"])
    geo.sort(key=lambda r: -r["score"])
    return {"business": biz.model_dump(), "intents": [i.model_dump() for i in intents],
            "seo_keywords": seo, "geo_prompts": geo}
