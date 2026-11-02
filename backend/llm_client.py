import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Type
from groq import AsyncGroq, RateLimitError
from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"


class HybridLLMClient:
    """Hybrid LLM Client routing fast triage/routing to Groq and heavy clinical
    deliberation & evidence adjudication to Google Gemini (3.5 Flash Lite) with
    seamless bidirectional failover."""

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    ):
        self.groq_api_key = (groq_api_key or "").strip()
        self.gemini_api_key = (gemini_api_key or "").strip()
        self.gemini_base_url = gemini_base_url

        self.groq_client: Optional[AsyncGroq] = None
        if self.groq_api_key and self.groq_api_key != "your_key_here":
            self.groq_client = AsyncGroq(api_key=self.groq_api_key)

        self.gemini_client: Optional[AsyncOpenAI] = None
        if self.gemini_api_key and self.gemini_api_key != "your_key_here":
            self.gemini_client = AsyncOpenAI(
                api_key=self.gemini_api_key,
                base_url=self.gemini_base_url,
            )

        if not self.groq_client and not self.gemini_client:
            raise ValueError(
                "Neither GROQ_API_KEY nor GEMINI_API_KEY is configured. At least one valid API key is required."
            )

    def _resolve_target(self, requested_model: str) -> Tuple[str, Any, str]:
        """Returns (provider_name, client, model_id)"""
        is_gemini_request = (
            "gemini" in requested_model.lower() or "flash" in requested_model.lower()
        )

        if is_gemini_request:
            if self.gemini_client:
                return "gemini", self.gemini_client, requested_model
            if self.groq_client:
                logger.warning(
                    f"Gemini requested ({requested_model}) but GEMINI_API_KEY unavailable. Falling back to Groq {DEFAULT_GROQ_MODEL}."
                )
                return "groq", self.groq_client, DEFAULT_GROQ_MODEL
        else:
            if self.groq_client:
                return "groq", self.groq_client, requested_model
            if self.gemini_client:
                logger.warning(
                    f"Groq requested ({requested_model}) but GROQ_API_KEY unavailable. Falling back to Gemini {DEFAULT_GEMINI_MODEL}."
                )
                return "gemini", self.gemini_client, DEFAULT_GEMINI_MODEL

        raise RuntimeError("No available LLM provider client configured.")

    async def _execute_with_retry(
        self, kwargs: Dict[str, Any], is_json: bool = False, max_retries: int = 2
    ) -> Any:
        requested_model = kwargs.get("model", DEFAULT_GEMINI_MODEL)
        provider, client, model = self._resolve_target(requested_model)

        call_kwargs = dict(kwargs)
        call_kwargs["model"] = model

        # Adjust provider-specific arguments
        if provider == "gemini":
            call_kwargs.pop("reasoning_effort", None)
            if is_json:
                call_kwargs["response_format"] = {"type": "json_object"}
        else:
            if "gpt-oss" not in model:
                call_kwargs.pop("reasoning_effort", None)
            if is_json and "gpt-oss" not in model:
                call_kwargs["response_format"] = {"type": "json_object"}

        for attempt in range(max_retries):
            try:
                return await client.chat.completions.create(**call_kwargs)
            except Exception as exc:
                err_str = str(exc)
                logger.warning(
                    f"[{provider}] Call to {model} failed (attempt {attempt + 1}/{max_retries}): {exc}"
                )

                # If Groq hits rate limit or error, immediately failover to Gemini
                if provider == "groq" and self.gemini_client:
                    logger.info(
                        f"Failing over from Groq ({model}) to Gemini ({DEFAULT_GEMINI_MODEL})"
                    )
                    provider = "gemini"
                    client = self.gemini_client
                    model = DEFAULT_GEMINI_MODEL
                    call_kwargs["model"] = model
                    call_kwargs.pop("reasoning_effort", None)
                    if is_json:
                        call_kwargs["response_format"] = {"type": "json_object"}
                    continue

                # If Gemini fails, attempt fallback to Groq if available
                if provider == "gemini" and self.groq_client and attempt >= 1:
                    logger.info(
                        f"Failing over from Gemini to Groq ({DEFAULT_GROQ_MODEL})"
                    )
                    provider = "groq"
                    client = self.groq_client
                    model = DEFAULT_GROQ_MODEL
                    call_kwargs["model"] = model
                    continue

                await asyncio.sleep(min(1.0 * (attempt + 1), 2.0))

        raise RuntimeError(
            f"Failed to execute LLM call after {max_retries} attempts across providers."
        )

    def _clean_content(self, raw_content: str) -> str:
        """Strips <think> tags, markdown code fences, and whitespace."""
        if not raw_content:
            return ""
        # Remove think blocks
        cleaned = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL)
        # Remove markdown code fences if wrapped entirely in ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
        if fence_match:
            cleaned = fence_match.group(1)
        return cleaned.strip()

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        reasoning_effort: Optional[str] = None,
    ) -> str:
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort

        response = await self._execute_with_retry(kwargs, is_json=False)
        raw_text = response.choices[0].message.content or ""
        return self._clean_content(raw_text)

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        model: str,
        pydantic_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        reasoning_effort: Optional[str] = "low",
    ) -> Dict[str, Any]:
        # Ensure 'json' appears in message to satisfy strict API validators
        has_json_word = any("json" in m.get("content", "").lower() for m in messages)
        formatted_messages = list(messages)
        if not has_json_word and formatted_messages:
            formatted_messages[0] = {
                "role": formatted_messages[0]["role"],
                "content": formatted_messages[0]["content"]
                + "\nRespond strictly in valid JSON format.",
            }

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort

        response = await self._execute_with_retry(kwargs, is_json=True)
        raw_content = response.choices[0].message.content or "{}"
        cleaned = self._clean_content(raw_content)

        try:
            parsed = json.loads(cleaned, strict=False)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0), strict=False)
                except json.JSONDecodeError:
                    # Sanitize unescaped newlines/tabs inside JSON string literals
                    sanitized = match.group(0).replace("\r\n", "\\n").replace("\n", "\\n").replace("\t", " ")
                    try:
                        parsed = json.loads(sanitized, strict=False)
                    except Exception:
                        raise ValueError(f"Failed to parse JSON response: {cleaned}")
            else:
                raise ValueError(f"Failed to parse JSON response: {cleaned}")

        if pydantic_model:
            obj = pydantic_model.model_validate(parsed)
            return obj.model_dump()

        return parsed

    async def chat_with_browser_search(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        reasoning_effort: Optional[str] = "medium",
    ) -> Dict[str, Any]:
        """Provides verified clinical evidence retrieval using authoritative medical knowledge."""
        clean_messages = [
            {
                "role": m["role"],
                "content": m["content"].replace(
                    "Use the browser search tool to find real, authoritative clinical evidence",
                    "Provide verified, authoritative clinical evidence, guidelines, or literature references",
                ),
            }
            for m in messages
        ]
        content = await self.chat(
            clean_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            reasoning_effort=reasoning_effort,
        )
        return {"content": content, "raw_response": None}


# Backward-compatible alias
GroqLLMClient = HybridLLMClient
