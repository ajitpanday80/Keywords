import os
from typing import Protocol, TypeVar

import anthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "claude-opus-5-5"


class LLM(Protocol):
    def parse(self, system: str, user: str, schema: type[T]) -> T: ...


class ClaudeLLM:
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("KWINTENT_MODEL", DEFAULT_MODEL)
        self.client = anthropic.Anthropic()

    def parse(self, system: str, user: str, schema: type[T]) -> T:
        resp = self.client.messages.parse(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
        )
        if resp.stop_reason == "refusal":
            raise RuntimeError(f"Model refused the request: {resp.stop_details}")
        if resp.stop_reason == "max_tokens":
            raise RuntimeError("Response truncated; lower --per-intent or --intents")
        return resp.parsed_output
