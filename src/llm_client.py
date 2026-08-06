"""
LLM client — one function to get a chat model, routed through OpenRouter.

OpenRouter exposes an OpenAI-compatible API in front of many providers
(Anthropic, OpenAI, Google, Meta, ...), so we can reuse langchain-openai's
client and just point it at OpenRouter's base_url with an OpenRouter key.
This is what makes model choice a one-line swap in Phase 2/3 nodes instead
of a different SDK per provider.

Model names follow OpenRouter's "provider/model" format, e.g.:
  "anthropic/claude-sonnet-4.5"
  "openai/gpt-4o"
  "google/gemini-2.5-flash"
See https://openrouter.ai/models for the full list.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Free tier for now (no OpenRouter credits needed) — swap to a paid model
# (e.g. "anthropic/claude-sonnet-4.5") once mentorship quality needs it.
# Note: nvidia/nemotron-3-super-120b-a12b:free was tried first but is a
# heavy "reasoning" model that burned its whole token budget on internal
# thinking without ever finishing on this task — swapped for a model that
# actually completes.
DEFAULT_MODEL = "openai/gpt-oss-20b:free"


def get_llm(model: str = DEFAULT_MODEL, temperature: float = 0.3, max_tokens: int = 1024) -> ChatOpenAI:
    # .strip() guards against a stray trailing newline/whitespace ending up
    # in the env var (e.g. from a copy-paste into a hosting dashboard) —
    # that alone is enough to make httpx reject the Authorization header
    # outright with a LocalProtocolError, before any network call happens.
    api_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip() or None
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file — "
            "get a key at https://openrouter.ai/keys"
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
        # Cloud-to-cloud calls (e.g. Render -> OpenRouter) can hit transient
        # connection blips that a local machine rarely sees. A longer
        # timeout + automatic retries handles that without masking a real,
        # persistent failure — it'll still raise after 3 attempts.
        timeout=60,
        max_retries=3,
    )
