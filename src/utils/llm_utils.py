import re
import yaml
import json
import logging
from typing import Any
from pathlib import Path
from pydantic_core import from_json

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]")
logger = logging.getLogger(__name__)


def _extract_json_value(raw: str) -> str:
    """
    Returns the first JSON value (object, array, string, number, boolean, null) found in `raw`.
    Raises if none is found.
    """
    # Try to find JSON object first
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        return m.group(0)

    # Try to find JSON array
    m = re.search(r"\[.*\]", raw, re.S)
    if m:
        return m.group(0)

    # Try to find JSON primitive values (boolean, number, string, null)
    m = re.search(r'\b(true|false|null)\b', raw, re.IGNORECASE)
    if m:
        return m.group(0)

    # Try to find numbers
    m = re.search(r'\b\d+(?:\.\d+)?\b', raw)
    if m:
        return m.group(0)

    # Try to find quoted strings
    m = re.search(r'"[^"]*"', raw)
    if m:
        return m.group(0)


def normalize_llm_json(text: str) -> str:
    # Replace Python-style literals with JSON
    text = re.sub(r'\bNone\b', 'null', text)
    text = re.sub(r'\bTrue\b', 'true', text)
    text = re.sub(r'\bFalse\b', 'false', text)
    return text

def extract_json_block(raw: str) -> Any:
    """
    Cleans and parses the JSON returned by get_text_generation_response_openai.
    - Removes Markdown fences and other noise
    - Strips illegal control characters
    - Delegates to pydantic_core.from_json for fast validation
    """
    try:
        # 1. Drop ```json / ``` fences if present
        cleaned = raw.replace("```json", "").replace("```", "")
        # 2. Pull out the JSON value (object, array, primitive)
        cleaned = _extract_json_value(cleaned)
        # 3. Remove any remaining control bytes that break json.loads()
        cleaned = _CONTROL_CHARS_RE.sub("", cleaned)

        #4. Normalize
        normalized = normalize_llm_json(cleaned)

        # 5. Parse
        return from_json(normalized)
    except Exception as exc:
        logger.error("Failed to parse LLM JSON: %s\nRAW: %s", exc, raw)
        raise ValueError("extract_json_block failed; request won't be processed") from exc


