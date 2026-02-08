# gemini_client.py — Gemini API wrapper for Aura AI
# Uses direct REST calls to Google Generative Language API.

import json
import base64
from typing import Optional, List, Dict
import httpx

from config import settings
from prompts import (
    BESTIE_SYSTEM_PROMPT,
    GURU_SYSTEM_PROMPT,
    RECEIPTS_SYSTEM_PROMPT,
    MATCH_SYSTEM_PROMPT,
    ROAST_SYSTEM_PROMPT,
    REMEDY_SYSTEM_PROMPT,
)

# ═══════════════════════════════════════════════════════════════
# GENERATION CONFIGS
# ═══════════════════════════════════════════════════════════════

BESTIE_CONFIG = {
    "temperature": 0.9,
    "topP": 0.95,
    "topK": 40,
    "maxOutputTokens": 800,
}

GURU_CONFIG = {
    "temperature": 0.7,
    "topP": 0.9,
    "topK": 30,
    "maxOutputTokens": 1200,
}

ANALYSIS_CONFIG = {
    "temperature": 0.8,
    "topP": 0.9,
    "topK": 30,
    "maxOutputTokens": 1500,
    "responseMimeType": "application/json",
}


# ═══════════════════════════════════════════════════════════════
# SAFETY SETTINGS (relaxed for astrology/relationship content)
# ═══════════════════════════════════════════════════════════════

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]


# ═══════════════════════════════════════════════════════════════
# CORE REQUEST HELPERS
# ═══════════════════════════════════════════════════════════════

async def _generate_content(model: str, contents: List[Dict], generation_config: Dict) -> str:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing")

    url = f"{settings.GEMINI_API_BASE}/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": contents,
        "generationConfig": generation_config,
        "safetySettings": SAFETY_SETTINGS,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code >= 400:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text}")

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini API returned no candidates")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
    return text if text else json.dumps(data)


def _history_to_contents(history: List[Dict]) -> List[Dict]:
    contents: List[Dict] = []
    for msg in history[-10:]:
        role = "user" if msg.get("role") == "user" else "model"
        content = msg.get("content", "")
        if content:
            contents.append({
                "role": role,
                "parts": [{"text": content}],
            })
    return contents


# ═══════════════════════════════════════════════════════════════
# CHAT FUNCTIONS (Vibe Check)
# ═══════════════════════════════════════════════════════════════

async def chat_bestie(
    message: str,
    user_name: str,
    user_sign: str,
    planetary_context: str,
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    system_prompt = BESTIE_SYSTEM_PROMPT.format(
        planetary_context=planetary_context,
        user_name=user_name,
        user_sign=user_sign.capitalize(),
    )

    contents = _history_to_contents(conversation_history or [])
    full_message = f"""[System Context - DO NOT repeat this to user]
{system_prompt}

[User's Message]
{message}"""

    contents.append({
        "role": "user",
        "parts": [{"text": full_message}],
    })

    return await _generate_content(settings.GEMINI_MODEL_FLASH, contents, BESTIE_CONFIG)


async def chat_guru(
    message: str,
    user_name: str,
    user_sign: str,
    planetary_context: str,
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    system_prompt = GURU_SYSTEM_PROMPT.format(
        planetary_context=planetary_context,
        user_name=user_name,
        user_sign=user_sign.capitalize(),
    )

    contents = _history_to_contents(conversation_history or [])
    full_message = f"""[System Context - DO NOT repeat this to user]
{system_prompt}

[User's Message]
{message}"""

    contents.append({
        "role": "user",
        "parts": [{"text": full_message}],
    })

    return await _generate_content(settings.GEMINI_MODEL_PRO, contents, GURU_CONFIG)


# ═══════════════════════════════════════════════════════════════
# RECEIPTS JUDGE (Vision + Text)
# ═══════════════════════════════════════════════════════════════

async def analyze_screenshot(
    image_base64: str,
    user_name: str,
    user_sign: str,
    planetary_context: str,
    context: Optional[str] = None,
) -> Dict:
    system_prompt = RECEIPTS_SYSTEM_PROMPT.format(
        planetary_context=planetary_context,
        user_name=user_name,
        user_sign=user_sign.capitalize(),
    )

    # Decode base64 image (supports data URLs)
    mime_type = "image/png"
    if image_base64.startswith("data:") and "," in image_base64:
        header, image_base64 = image_base64.split(",", 1)
        header = header[5:]  # strip 'data:'
        if ";" in header:
            mime_type = header.split(";", 1)[0] or mime_type
    elif "," in image_base64:
        image_base64 = image_base64.split(",", 1)[1]

    image_base64 = image_base64.strip()
    # Validate base64
    base64.b64decode(image_base64, validate=True)

    user_context = f"\nUser's additional context: {context}" if context else ""

    prompt = f"""{system_prompt}
{user_context}

Analyze this chat screenshot. Read every message, note timestamps, and cross-reference with the planetary data above. Return your analysis as JSON."""

    contents = [{
        "role": "user",
        "parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": mime_type, "data": image_base64}},
        ],
    }]

    response_text = await _generate_content(settings.GEMINI_MODEL_PRO, contents, ANALYSIS_CONFIG)

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        text = response_text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = {
                "toxic_score": 65,
                "red_flags": [{"flag": "Could not fully analyze", "severity": 5, "planetary_cause": "Mercury interference"}],
                "verdict": text[:500],
                "planetary_context": planetary_context[:200],
                "advice": "Try uploading a clearer screenshot for better analysis.",
                "timestamp_analysis": "",
                "shareable_summary": "The cosmos needs a better screenshot 📸"
            }

    return result


# ═══════════════════════════════════════════════════════════════
# MATCH CHECK (Compatibility)
# ═══════════════════════════════════════════════════════════════

ELEMENT_MAP = {
    "aries": "Fire", "leo": "Fire", "sagittarius": "Fire",
    "taurus": "Earth", "virgo": "Earth", "capricorn": "Earth",
    "gemini": "Air", "libra": "Air", "aquarius": "Air",
    "cancer": "Water", "scorpio": "Water", "pisces": "Water",
}

async def check_compatibility(
    user_sign: str,
    crush_sign: str,
    user_name: str = "User",
) -> Dict:
    user_element = ELEMENT_MAP.get(user_sign.lower(), "Unknown")
    crush_element = ELEMENT_MAP.get(crush_sign.lower(), "Unknown")

    prompt = MATCH_SYSTEM_PROMPT.format(
        user_sign=user_sign.capitalize(),
        user_element=user_element,
        crush_sign=crush_sign.capitalize(),
        crush_element=crush_element,
    )

    contents = [{
        "role": "user",
        "parts": [{"text": prompt}],
    }]

    response_text = await _generate_content(settings.GEMINI_MODEL_FLASH, contents, ANALYSIS_CONFIG)

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        text = response_text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = {
                "overall_score": 65,
                "toxic_level": "Medium",
                "verdict": f"{user_sign.capitalize()} and {crush_sign.capitalize()} — it's complicated. The stars are still deliberating.",
                "element_dynamics": f"{user_element} meets {crush_element}",
                "breakdown": {"emotional": 60, "physical": 65, "intellectual": 55, "spiritual": 50},
                "advice": "Proceed with cosmic caution.",
                "shareable_summary": f"{user_sign.capitalize()} × {crush_sign.capitalize()} = cosmic chaos 🌀"
            }

    return result


# ═══════════════════════════════════════════════════════════════
# ROAST GENERATOR
# ═══════════════════════════════════════════════════════════════

async def generate_roast(
    sign: str,
    planetary_context: str,
    context: Optional[str] = None,
) -> str:
    prompt = ROAST_SYSTEM_PROMPT.format(
        planetary_context=planetary_context,
        sign=sign.capitalize(),
        context=context or "general roast",
    )

    contents = [{
        "role": "user",
        "parts": [{"text": prompt}],
    }]

    response_text = await _generate_content(
        settings.GEMINI_MODEL_FLASH,
        contents,
        {"temperature": 0.95, "maxOutputTokens": 200}
    )

    return response_text


# ═══════════════════════════════════════════════════════════════
# REMEDY GENERATOR
# ═══════════════════════════════════════════════════════════════

async def generate_remedy(
    sign: str,
    planetary_context: str,
    concern: Optional[str] = None,
) -> Dict:
    prompt = REMEDY_SYSTEM_PROMPT.format(
        planetary_context=planetary_context,
        sign=sign.capitalize(),
        concern=concern or "general wellbeing",
    )

    contents = [{
        "role": "user",
        "parts": [{"text": prompt}],
    }]

    response_text = await _generate_content(settings.GEMINI_MODEL_PRO, contents, ANALYSIS_CONFIG)

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        text = response_text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(text[start:end])
        else:
            result = {
                "title": "General Wellness Upay",
                "description": "Light a ghee diya at sunset and meditate for 5 minutes.",
                "icon": "🪔",
                "for_concern": concern or "general",
                "planetary_basis": "Default remedy for cosmic alignment.",
                "timing": "Today at sunset"
            }

    return result
