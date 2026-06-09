from __future__ import annotations

import json
import os
import re
from typing import Any, Callable, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from .settings import load_environment


T = TypeVar("T")


PROVIDER_ENV = {
    "openai": ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL", "gpt-4o-mini"),
    "aimlapi": ("AIMLAPI_API_KEY", "AIMLAPI_BASE_URL", "AIMLAPI_MODEL", "gpt-4o-mini"),
    "featherless": ("FEATHERLESS_API_KEY", "FEATHERLESS_BASE_URL", "FEATHERLESS_MODEL", "gpt-4o-mini"),
    "custom": ("CUSTOM_API_KEY", "CUSTOM_BASE_URL", "CUSTOM_MODEL", "gpt-4o-mini"),
}


def strip_json_fences(content: str) -> str:
    text = content.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return fence.group(1).strip() if fence else text


class LLMClient:
    def __init__(self) -> None:
        load_environment()
        self.provider = os.getenv("LLM_PROVIDER", "mock").strip().lower() or "mock"
        self.api_key, self.base_url, self.model = self._resolve_provider()

    @property
    def is_configured(self) -> bool:
        return self.provider != "mock" and bool(self.api_key)

    def _resolve_provider(self) -> tuple[str | None, str | None, str]:
        if self.provider not in PROVIDER_ENV:
            return None, None, "mock"
        key_env, base_env, model_env, default_model = PROVIDER_ENV[self.provider]
        api_key = os.getenv(key_env)
        base_url = os.getenv(base_env) or None
        model = os.getenv(model_env) or os.getenv("OPENAI_MODEL") or default_model
        return api_key, base_url, model

    def generate_json(
        self,
        system_prompt: str,
        user_payload: dict[str, Any],
        fallback_fn: Callable[[], T],
        schema_model: type[BaseModel] | None = None,
    ) -> T | dict[str, Any]:
        if not self.is_configured:
            return fallback_fn()

        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload)},
                ],
            )
            raw = response.choices[0].message.content or "{}"
            parsed = json.loads(strip_json_fences(raw))
            if schema_model is None:
                return parsed
            return schema_model.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError, Exception) as exc:
            print(f"LLM provider {self.provider} failed; falling back to deterministic logic: {exc}")
            return fallback_fn()


def get_langchain_model_kwargs() -> dict[str, Any]:
    load_environment()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower() or "mock"
    if provider not in PROVIDER_ENV:
        provider = "openai"
    key_env, base_env, model_env, default_model = PROVIDER_ENV[provider]
    api_key = os.getenv(key_env) or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv(base_env) or os.getenv("OPENAI_BASE_URL") or None
    model = os.getenv(model_env) or os.getenv("OPENAI_MODEL") or default_model
    kwargs: dict[str, Any] = {"model": model}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    return kwargs
