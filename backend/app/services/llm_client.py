"""
Unified LLM client — routes to the correct provider based on LLM_PROVIDER setting.

Supported providers
-------------------
- "google"  : Google AI Studio via google-generativeai SDK
- "ollama"  : Local Ollama via httpx (no extra SDK needed)

Usage
-----
    from app.services.llm_client import llm_client

    text = await llm_client.complete("Summarise this email…")
    json_str = await llm_client.complete("Extract JSON…", json_mode=True)
"""

from __future__ import annotations

import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin async wrapper that normalises Google AI Studio and Ollama calls."""

    # ------------------------------------------------------------------
    # Google AI Studio
    # ------------------------------------------------------------------

    async def _complete_google(self, prompt: str, json_mode: bool) -> str:
        """Call Gemini via the google-generativeai SDK."""
        try:
            import google.generativeai as genai  # lazy import — only needed for google provider
        except ImportError:
            raise RuntimeError(
                "google-generativeai is not installed. "
                "Run: pip install google-generativeai"
            )

        genai.configure(api_key=settings.GEMINI_API_KEY)

        generation_config: dict = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=generation_config if generation_config else None,
        )

        response = model.generate_content(prompt)
        return response.text.strip()

    # ------------------------------------------------------------------
    # Ollama (local)
    # ------------------------------------------------------------------

    async def _complete_ollama(self, prompt: str, json_mode: bool) -> str:
        """Call a locally running Ollama instance via its HTTP API."""
        payload: dict = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        if json_mode:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def complete(self, prompt: str, json_mode: bool = False) -> str:
        """
        Send *prompt* to the configured LLM and return the raw text response.

        Parameters
        ----------
        prompt    : The full prompt string (system + user combined).
        json_mode : When True, instruct the model to respond with valid JSON only.

        Returns
        -------
        str — raw model output (caller responsible for parsing JSON if needed).
        """
        provider = settings.LLM_PROVIDER.lower()
        logger.debug("LLMClient.complete | provider=%s | json_mode=%s", provider, json_mode)

        if provider == "google":
            return await self._complete_google(prompt, json_mode)
        elif provider == "ollama":
            return await self._complete_ollama(prompt, json_mode)
        else:
            raise ValueError(
                f"Unknown LLM_PROVIDER '{provider}'. "
                "Valid options: 'google' | 'ollama'"
            )

    async def complete_json(self, prompt: str) -> dict:
        """
        Convenience wrapper — calls complete() with json_mode=True and parses the result.

        Raises
        ------
        ValueError if the model returns non-JSON text.
        """
        raw = await self.complete(prompt, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            # Attempt to salvage by stripping markdown fences the model may add
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                logger.error("LLM returned non-JSON output:\n%s", raw)
                raise ValueError(f"LLM response is not valid JSON: {exc}") from exc


# Module-level singleton — import this everywhere
llm_client = LLMClient()
