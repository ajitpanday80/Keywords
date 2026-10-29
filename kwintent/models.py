from typing import Literal

from pydantic import BaseModel

IntentType = Literal[
    "learn", "compare", "buy", "fix_problem", "find_local", "find_brand", "do_task"
]
Stage = Literal["awareness", "consideration", "decision", "retention"]
VolumeBand = Literal["<10", "10-100", "100-1k", "1k-10k", "10k-100k", "100k+"]
Confidence = Literal["low", "medium", "high"]
Difficulty = Literal["low", "medium", "high", "very_high"]
Risk = Literal["low", "medium", "high"]
Demand = Literal["rare", "occasional", "common", "very_common"]

VOLUME_BANDS: list[str] = ["<10", "10-100", "100-1k", "1k-10k", "10k-100k", "100k+"]


class Business(BaseModel):
    description: str
    audience: str = ""
    market: str = "US, English"
    site_strength: Literal["new", "growing", "established"] = "new"


class Intent(BaseModel):
    id: str
    name: str
    searcher_problem: str  # the underlying job the person is trying to get done
    persona: str
    intent_type: IntentType
    journey_stage: Stage
    business_fit: int  # 1-5: how well serving this intent leads to the business's goals
    rationale: str


class IntentMap(BaseModel):
    intents: list[Intent]


class SeoKeyword(BaseModel):
    keyword: str
    volume_band: VolumeBand
    volume_confidence: Confidence
    difficulty: Difficulty
    difficulty_reason: str
    expected_serp: str  # who/what likely ranks (forums, big brands, tools, ...)
    ai_overview_risk: Risk  # chance an AI answer absorbs the click
    content_format: str
    business_value: int  # 1-5


class GeoPrompt(BaseModel):
    prompt: str  # a natural-language question as typed to an AI assistant
    demand: Demand
    citation_difficulty: Difficulty
    likely_cited_sources: str
    content_format: str
    business_value: int  # 1-5


class IntentExpansion(BaseModel):
    seo_keywords: list[SeoKeyword]
    geo_prompts: list[GeoPrompt]
