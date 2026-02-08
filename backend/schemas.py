# schemas.py — Pydantic models for Aura AI API

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════

class ChatMode(str, Enum):
    bestie = "bestie"
    guru = "guru"


class ZodiacSign(str, Enum):
    aries = "aries"
    taurus = "taurus"
    gemini = "gemini"
    cancer = "cancer"
    leo = "leo"
    virgo = "virgo"
    libra = "libra"
    scorpio = "scorpio"
    sagittarius = "sagittarius"
    capricorn = "capricorn"
    aquarius = "aquarius"
    pisces = "pisces"


class Element(str, Enum):
    fire = "Fire"
    earth = "Earth"
    air = "Air"
    water = "Water"


# ═══════════════════════════════════════════════════════════════
# USER
# ═══════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    sign: ZodiacSign
    dob: date
    birth_time: Optional[time] = None
    birth_place: Optional[str] = None  # For accurate house calculations


class UserProfile(BaseModel):
    id: str
    name: str
    sign: ZodiacSign
    dob: date
    birth_time: Optional[time]
    is_premium: bool = False
    messages_today: int = 0
    created_at: datetime


# ═══════════════════════════════════════════════════════════════
# CHAT (Vibe Check)
# ═══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Request body for the Vibe Check chat endpoint."""
    user_id: str
    message: str = Field(..., min_length=1, max_length=2000)
    mode: ChatMode = ChatMode.bestie
    conversation_history: Optional[List[dict]] = Field(default_factory=list)  # [{role, content}]


class ChatResponse(BaseModel):
    reply: str
    mode: ChatMode
    planetary_context: Optional[str] = None  # Current transit summary
    tokens_used: Optional[int] = None
    is_free: bool = True  # False if counted against free limit


# ═══════════════════════════════════════════════════════════════
# RECEIPTS JUDGE (Screenshot Analysis)
# ═══════════════════════════════════════════════════════════════

class ReceiptsRequest(BaseModel):
    user_id: str
    image_base64: str  # Base64 encoded screenshot
    context: Optional[str] = None  # "This is my ex" etc.


class RedFlagDetail(BaseModel):
    flag: str           # "Late night text"
    severity: int       # 1-10
    planetary_cause: str  # "Mars-Venus clash at 2:03 AM"


class ReceiptsResponse(BaseModel):
    toxic_score: int = Field(..., ge=0, le=100)
    red_flags: List[RedFlagDetail]
    verdict: str          # Main analysis paragraph
    planetary_context: str  # What was happening in the sky
    advice: str           # What to do about it
    timestamp_analysis: Optional[str] = None  # Time-based insights
    shareable_summary: str  # One-liner for sharing


# ═══════════════════════════════════════════════════════════════
# MATCH CHECK (Compatibility)
# ═══════════════════════════════════════════════════════════════

class MatchRequest(BaseModel):
    user_id: str
    user_sign: ZodiacSign
    crush_sign: ZodiacSign
    user_dob: Optional[date] = None
    crush_dob: Optional[date] = None  # If known, more accurate


class CompatibilityBreakdown(BaseModel):
    emotional: int = Field(..., ge=0, le=100)
    physical: int = Field(..., ge=0, le=100)
    intellectual: int = Field(..., ge=0, le=100)
    spiritual: int = Field(..., ge=0, le=100)


class MatchResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    toxic_level: str  # "Low", "Medium", "High"
    verdict: str      # The fun analysis
    element_dynamics: str  # "Fire × Water = Steam"
    breakdown: CompatibilityBreakdown
    advice: str
    shareable_summary: str


# ═══════════════════════════════════════════════════════════════
# COSMIC BATTERY
# ═══════════════════════════════════════════════════════════════

class BatteryRequest(BaseModel):
    user_id: str
    sign: ZodiacSign
    dob: date
    birth_time: Optional[time] = None


class TransitInfo(BaseModel):
    planet: str
    status: str       # "Retrograde", "Direct", "Transit"
    sign: str         # Which zodiac sign planet is in
    house: Optional[int] = None  # Which house for the user
    effect: str       # Brief description


class BatteryResponse(BaseModel):
    percentage: int = Field(..., ge=0, le=100)
    level: str        # "peak", "good", "neutral", "low", "critical"
    message: str      # Main message
    detailed_reason: str
    active_transits: List[TransitInfo]
    remedy: Optional[str] = None  # If battery is low


# ═══════════════════════════════════════════════════════════════
# ROAST
# ═══════════════════════════════════════════════════════════════

class RoastRequest(BaseModel):
    user_id: Optional[str] = None
    sign: ZodiacSign
    context: Optional[str] = None  # "roast my love life"


class RoastResponse(BaseModel):
    roast: str
    planetary_context: str


# ═══════════════════════════════════════════════════════════════
# REMEDY / UPAY
# ═══════════════════════════════════════════════════════════════

class RemedyRequest(BaseModel):
    user_id: str
    sign: ZodiacSign
    concern: Optional[str] = None  # "career", "love", "health"


class RemedyResponse(BaseModel):
    title: str
    description: str
    icon: str
    for_concern: str
    planetary_basis: str  # Why this remedy works astrologically
    timing: str           # "Tonight at sunset", "Thursday morning"


# ═══════════════════════════════════════════════════════════════
# PAYMENTS
# ═══════════════════════════════════════════════════════════════

class CreateOrderRequest(BaseModel):
    user_id: str
    item: str  # "receipts_single", "deep_dive_report", "instant_upay", "inner_circle"
    amount: int  # In paise (₹29 = 2900)


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str = "INR"
    razorpay_order_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
