from .models import Business, Intent

SYSTEM = """You are an SEO and generative-engine-optimization (GEO) strategist.
You have NO access to search volume, keyword difficulty, SERP or AI-citation data. Every
number you produce is an estimate from your general knowledge, and your knowledge may be
out of date. Therefore:
- Use only the coarse bands in the schema. Never imply precision you lack.
- Mark volume_confidence "low" whenever you are guessing; most long-tail terms deserve it.
- Judge difficulty relative to the stated site strength, using what usually ranks for this
  kind of query (big brands, forums, aggregators, official docs) and how commercial it is.
- Prefer being consistent across items over being exact: relative ordering matters more
  than absolute levels.
- Do not invent statistics, tools, brands or sources. If unsure who would rank, say so.
Think in terms of searcher intent (the job being done), not word variants of a seed."""


def _biz(b: Business) -> str:
    return (f"Business: {b.description}\nAudience: {b.audience or 'unspecified'}\n"
            f"Market/language: {b.market}\nSite strength: {b.site_strength}")


def intent_map_prompt(b: Business, n: int) -> str:
    return (f"{_biz(b)}\n\nBuild an intent map of about {n} distinct searcher intents "
            "relevant to this business. Each intent is a distinct job/problem a real person "
            "has, not a keyword. Cover different intent types and journey stages, include "
            "intents the business might overlook (problems adjacent to the product, "
            "comparisons, pre-purchase worries, post-purchase issues), and rate "
            "business_fit 1-5 honestly (5 = directly leads to revenue/goal). "
            "Use short snake_case ids.")


def expansion_prompt(b: Business, i: Intent, n_seo: int, n_geo: int) -> str:
    return (f"{_biz(b)}\n\nIntent: {i.name} ({i.intent_type}, {i.journey_stage})\n"
            f"Persona: {i.persona}\nProblem: {i.searcher_problem}\n\n"
            f"List ~{n_seo} SEO keywords real people would type for this intent, spanning "
            "head and long-tail phrasings, plus ~"
            f"{n_geo} GEO prompts: full natural-language questions or requests someone "
            "would give an AI assistant (ChatGPT, Claude, Perplexity, AI Overviews) for "
            "this intent, including multi-constraint and 'recommend me X for Y' styles. "
            "For GEO there is no volume data anywhere, so 'demand' is a rough guess of how "
            "commonly such a prompt is asked. Estimate each item per the schema.")
