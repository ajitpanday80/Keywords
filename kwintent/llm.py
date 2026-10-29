import json
import os
import re
import urllib.error
import urllib.request
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/auto"


class LLM(Protocol):
    def parse(self, system: str, user: str, schema: type[T]) -> T: ...


def _extract_json(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1] if start != -1 and end > start else text


class OpenRouterLLM:
    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set OPENROUTER_API_KEY (or paste a key in the web UI).")

    def _chat(self, messages: list[dict]) -> str:
        body = json.dumps({"model": self.model, "messages": messages,
                           "max_tokens": 16000}).encode()
        req = urllib.request.Request(URL, body, {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "kwintent"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"OpenRouter {e.code}: {e.read().decode()[:300]}") from e
        if "error" in data:
            raise RuntimeError(f"OpenRouter error: {data['error']}")
        choice = data["choices"][0]
        if choice.get("finish_reason") == "length":
            raise RuntimeError("Response truncated; lower the number of intents/items.")
        return choice["message"]["content"] or ""

    def parse(self, system: str, user: str, schema: type[T]) -> T:
        # Not every OpenRouter model supports json_schema mode, so the schema goes in
        # the prompt and the reply is validated locally, with one corrective retry.
        sys = (f"{system}\n\nRespond with ONLY a JSON object (no prose, no code fences) "
               f"matching this JSON Schema:\n{json.dumps(schema.model_json_schema())}")
        messages = [{"role": "system", "content": sys}, {"role": "user", "content": user}]
        for attempt in range(2):
            text = self._chat(messages)
            try:
                return schema.model_validate_json(_extract_json(text))
            except (ValidationError, ValueError) as e:
                if attempt == 1:
                    raise RuntimeError(f"Model returned invalid JSON: {str(e)[:300]}") from e
                messages += [{"role": "assistant", "content": text},
                             {"role": "user", "content": f"Invalid: {str(e)[:500]}\n"
                              "Return corrected JSON only."}]
