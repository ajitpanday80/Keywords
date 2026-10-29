"""Canned LLM for UI/offline testing. Output is SAMPLE DATA, not real estimates."""
from .models import GeoPrompt, Intent, IntentExpansion, IntentMap, SeoKeyword


def _i(id, name, prob, persona, typ, stage, fit):
    return Intent(id=id, name=name, searcher_problem=prob, persona=persona,
                  intent_type=typ, journey_stage=stage, business_fit=fit, rationale="sample")


INTENTS = [
    _i("compare_tools", "Compare construction PM software", "Pick a tool before committing budget",
       "Owner of a 10-person contractor", "compare", "consideration", 5),
    _i("replace_spreadsheets", "Escape spreadsheet chaos", "Stop tracking jobs in Excel and email",
       "Operations manager", "fix_problem", "awareness", 4),
    _i("change_orders", "Handle change orders properly", "Document and get paid for scope changes",
       "Site manager", "learn", "awareness", 3),
    _i("price_check", "Understand software pricing", "Know total cost before a demo",
       "Small-firm owner", "buy", "decision", 5),
    _i("daily_logs", "Write daily site reports faster", "Cut paperwork at end of day",
       "Superintendent", "do_task", "awareness", 4),
]

_S = lambda k, v, c, d, r, serp, ai, fmt, bv: SeoKeyword(
    keyword=k, volume_band=v, volume_confidence=c, difficulty=d, difficulty_reason=r,
    expected_serp=serp, ai_overview_risk=ai, content_format=fmt, business_value=bv)
_G = lambda p, d, cd, src, fmt, bv: GeoPrompt(
    prompt=p, demand=d, citation_difficulty=cd, likely_cited_sources=src,
    content_format=fmt, business_value=bv)

EXP = {
    "compare_tools": ([
        _S("best construction project management software", "10k-100k", "medium", "very_high", "Dominated by review aggregators", "G2, Capterra, big vendors", "medium", "Comparison hub", 5),
        _S("procore alternatives for small contractors", "1k-10k", "medium", "medium", "Alt-pages are contested but niche", "Vendor blogs, listicles", "medium", "Alternatives page", 5),
        _S("construction software for small business", "1k-10k", "low", "high", "Broad, commercial", "Aggregators", "medium", "Landing page", 4),
        _S("buildertrend vs jobtread", "100-1k", "low", "medium", "Head-to-head, few strong pages", "Vendor + review sites", "low", "Versus page", 4),
    ], [
        _G("What's the best project management tool for a 10-person general contractor?", "common", "high", "Review sites, vendor docs", "Comparison table + FAQ", 5),
        _G("Is there a cheaper alternative to Procore for small builders?", "common", "medium", "Vendor blogs, forums", "Alternatives guide", 5),
    ]),
    "replace_spreadsheets": ([
        _S("how to manage construction projects in excel", "1k-10k", "medium", "medium", "Templates and how-tos", "Template sites, YouTube", "medium", "Guide + template", 4),
        _S("construction job tracking spreadsheet", "1k-10k", "low", "low", "Thin content ranks", "Template blogs", "low", "Free template", 3),
        _S("why excel fails for construction scheduling", "10-100", "low", "low", "Few direct answers", "Blogs, forums", "low", "Opinion article", 4),
    ], [
        _G("I run jobs out of spreadsheets and email. What should I switch to?", "occasional", "medium", "Forums, vendor blogs", "Migration guide", 5),
        _G("How do I move from Excel to a construction management app?", "occasional", "low", "How-to articles", "Step-by-step guide", 4),
    ]),
    "change_orders": ([
        _S("construction change order template", "10k-100k", "medium", "high", "Template intent, many strong sites", "Template sites, associations", "medium", "Template + guide", 3),
        _S("how to price a change order", "1k-10k", "low", "medium", "Mixed quality", "Trade blogs", "medium", "How-to", 3),
        _S("who pays for change orders when owner changes scope", "100-1k", "low", "low", "Long-tail question", "Forums, law blogs", "low", "Explainer", 3),
    ], [
        _G("How do I write a change order that actually gets approved?", "common", "medium", "Trade blogs, law firms", "Checklist", 3),
    ]),
    "price_check": ([
        _S("construction management software pricing", "1k-10k", "medium", "high", "Commercial, vendor-heavy", "Vendors, aggregators", "medium", "Pricing explainer", 5),
        _S("how much does buildertrend cost", "1k-10k", "medium", "medium", "Brand query", "Vendor, review sites", "high", "Pricing breakdown", 4),
        _S("free construction project management software", "10k-100k", "medium", "very_high", "High competition, low intent", "Listicles", "medium", "Free-tier comparison", 2),
    ], [
        _G("What does construction project management software typically cost per month?", "common", "medium", "Review sites, vendors", "Pricing table", 5),
    ]),
    "daily_logs": ([
        _S("construction daily report template", "10k-100k", "medium", "high", "Template intent", "Template sites, vendors", "medium", "Template + app CTA", 4),
        _S("how to write a daily log for a construction site", "1k-10k", "low", "low", "Informational long-tail", "Blogs, YouTube", "medium", "How-to", 4),
        _S("daily log app for superintendents", "100-1k", "low", "low", "Niche, app-store heavy", "App stores, vendors", "low", "Landing page", 5),
    ], [
        _G("What should a superintendent include in a daily construction log?", "common", "low", "Trade blogs, templates", "Checklist", 4),
        _G("Best app for daily site reports with photos?", "common", "medium", "App reviews, vendor pages", "Comparison", 5),
    ]),
}


class DemoLLM:
    def parse(self, system, user, schema):
        if schema is IntentMap:
            return IntentMap(intents=INTENTS)
        for iid, (kws, gps) in EXP.items():
            if next(i for i in INTENTS if i.id == iid).name in user:
                return IntentExpansion(seo_keywords=kws, geo_prompts=gps)
        raise ValueError("unknown intent")
