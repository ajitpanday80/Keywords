from kwintent import pipeline, report, scoring
from kwintent.models import (Business, Intent, IntentExpansion, IntentMap,
                             SeoKeyword, GeoPrompt)


def kw(text, band="1k-10k", diff="medium"):
    return SeoKeyword(keyword=text, volume_band=band, volume_confidence="low",
                      difficulty=diff, difficulty_reason="x", expected_serp="x",
                      ai_overview_risk="low", content_format="guide", business_value=4)


class Fake:
    def parse(self, system, user, schema):
        if schema is IntentMap:
            return IntentMap(intents=[
                Intent(id=i, name=i, searcher_problem="p", persona="x",
                       intent_type="learn", journey_stage="awareness",
                       business_fit=4, rationale="r") for i in ("a", "b")])
        return IntentExpansion(
            seo_keywords=[kw("Same Query"), kw("unique " + user[-5:], "100k+", "low")],
            geo_prompts=[GeoPrompt(prompt="best x?", demand="common",
                                   citation_difficulty="low", likely_cited_sources="s",
                                   content_format="faq", business_value=4)])


def test_pipeline_dedupes_and_sorts(tmp_path):
    res = pipeline.run(Fake(), Business(description="d"))
    kws = [k["keyword"].lower() for k in res["seo_keywords"]]
    assert kws.count("same query") == 1
    assert len(res["geo_prompts"]) == 1
    scores = [k["score"] for k in res["seo_keywords"]]
    assert scores == sorted(scores, reverse=True)
    report.write(res, tmp_path)
    assert "Claude's estimates" in (tmp_path / "report.md").read_text()


def test_scoring_monotonic():
    base = dict(confidence="high", ai_risk="low", business_value=5, business_fit=5)
    assert scoring.seo_score("100k+", difficulty="low", **base) > \
        scoring.seo_score("100-1k", difficulty="low", **base)
    assert scoring.seo_score("1k-10k", difficulty="low", **base) > \
        scoring.seo_score("1k-10k", difficulty="very_high", **base)
