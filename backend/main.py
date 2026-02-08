# main.py — Aura AI FastAPI Backend
# Run: uvicorn main:app --reload --port 8000

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, date
import hmac
import hashlib
import httpx
from pathlib import Path

from config import settings
from schemas import (
    ChatRequest, ChatResponse, ChatMode,
    ReceiptsRequest, ReceiptsResponse, RedFlagDetail,
    MatchRequest, MatchResponse, CompatibilityBreakdown,
    BatteryRequest, BatteryResponse, TransitInfo,
    RoastRequest, RoastResponse,
    RemedyRequest, RemedyResponse,
    UserCreate,
    CreateOrderRequest, CreateOrderResponse, VerifyPaymentRequest,
)
from astro_engine import (
    format_planetary_context,
    calculate_cosmic_battery,
    get_current_transits,
)
from gemini_client import (
    chat_bestie,
    chat_guru,
    analyze_screenshot,
    check_compatibility,
    generate_roast,
    generate_remedy,
)
from storage import (
    init_db,
    create_user,
    get_user,
    increment_messages_today,
    increment_receipts_today,
    add_receipts_credit,
    consume_receipts_credit,
    create_order,
    get_order_by_razorpay_id,
    mark_order_paid,
    set_user_premium,
)

# ═══════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="Aura AI — Cosmic Bestie API",
    description="Vedic Astrology × Gen Z Energy. No Filter. No Judgement.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve built frontend if available
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════


def _require_user(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _is_premium(user: dict) -> bool:
    return bool(user.get("is_premium"))


# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "app": "Aura AI",
        "tagline": "Your Cosmic Bestie. No Filter. No Judgement.",
        "status": "✦ Online",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ═══════════════════════════════════════════════════════════════
# ROUTE 1: VIBE CHECK CHAT
# POST /api/chat
# ═══════════════════════════════════════════════════════════════

@app.post("/api/chat", response_model=ChatResponse)
async def vibe_check(req: ChatRequest):
    try:
        user = _require_user(req.user_id)

        if not _is_premium(user) and user["messages_today"] >= settings.FREE_MESSAGES_PER_DAY:
            raise HTTPException(status_code=402, detail="Free message limit reached")

        user_sign = user["sign"]
        user_dob = date.fromisoformat(user["dob"])
        user_name = user["name"]

        planetary_context = format_planetary_context(user_sign, user_dob)

        if req.mode == ChatMode.bestie:
            reply = await chat_bestie(
                message=req.message,
                user_name=user_name,
                user_sign=user_sign,
                planetary_context=planetary_context,
                conversation_history=req.conversation_history or [],
            )
        else:
            reply = await chat_guru(
                message=req.message,
                user_name=user_name,
                user_sign=user_sign,
                planetary_context=planetary_context,
                conversation_history=req.conversation_history or [],
            )

        increment_messages_today(user["id"])

        return ChatResponse(
            reply=reply,
            mode=req.mode,
            planetary_context=planetary_context[:200],
            is_free=not _is_premium(user),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cosmic interference: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 2: RECEIPTS JUDGE (Screenshot Analysis)
# POST /api/receipts
# ═══════════════════════════════════════════════════════════════

@app.post("/api/receipts", response_model=ReceiptsResponse)
async def receipts_judge(req: ReceiptsRequest):
    try:
        user = _require_user(req.user_id)

        if not _is_premium(user):
            if user["receipts_today"] < settings.FREE_RECEIPTS_PER_DAY:
                increment_receipts_today(user["id"])
            elif consume_receipts_credit(user["id"]):
                pass
            else:
                raise HTTPException(status_code=402, detail="Receipts limit reached")

        user_sign = user["sign"]
        user_dob = date.fromisoformat(user["dob"])
        user_name = user["name"]

        planetary_context = format_planetary_context(user_sign, user_dob)

        result = await analyze_screenshot(
            image_base64=req.image_base64,
            user_name=user_name,
            user_sign=user_sign,
            planetary_context=planetary_context,
            context=req.context,
        )

        red_flags = []
        for rf in result.get("red_flags", []):
            red_flags.append(RedFlagDetail(
                flag=rf.get("flag", "Unknown"),
                severity=rf.get("severity", 5),
                planetary_cause=rf.get("planetary_cause", "Cosmic mystery"),
            ))

        return ReceiptsResponse(
            toxic_score=result.get("toxic_score", 50),
            red_flags=red_flags,
            verdict=result.get("verdict", "The cosmos is processing..."),
            planetary_context=result.get("planetary_context", ""),
            advice=result.get("advice", "Trust the process."),
            timestamp_analysis=result.get("timestamp_analysis"),
            shareable_summary=result.get("shareable_summary", "Analyzed by Aura AI ✦"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision disrupted: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 3: MATCH CHECK (Compatibility)
# POST /api/match
# ═══════════════════════════════════════════════════════════════

@app.post("/api/match", response_model=MatchResponse)
async def match_check(req: MatchRequest):
    try:
        _require_user(req.user_id)

        result = await check_compatibility(
            user_sign=req.user_sign.value,
            crush_sign=req.crush_sign.value,
            user_name="User",
        )

        breakdown = result.get("breakdown", {})

        return MatchResponse(
            overall_score=result.get("overall_score", 65),
            toxic_level=result.get("toxic_level", "Medium"),
            verdict=result.get("verdict", "The stars are deliberating..."),
            element_dynamics=result.get("element_dynamics", ""),
            breakdown=CompatibilityBreakdown(
                emotional=breakdown.get("emotional", 60),
                physical=breakdown.get("physical", 60),
                intellectual=breakdown.get("intellectual", 60),
                spiritual=breakdown.get("spiritual", 60),
            ),
            advice=result.get("advice", "Proceed with cosmic caution."),
            shareable_summary=result.get("shareable_summary", "Matched by Aura AI ✦"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synastry error: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 4: COSMIC BATTERY
# POST /api/battery
# ═══════════════════════════════════════════════════════════════

@app.post("/api/battery", response_model=BatteryResponse)
async def cosmic_battery(req: BatteryRequest):
    try:
        user = _require_user(req.user_id)
        user_sign = user["sign"]
        user_dob = date.fromisoformat(user["dob"])

        battery = calculate_cosmic_battery(user_sign, user_dob)
        transits = get_current_transits(user_sign, user_dob)

        transit_list = []
        for t in transits:
            effect = ""
            if t.planet == "Moon":
                effect = "Emotional energy" + (" disrupted" if t.house_from_moon in [6, 8, 12] else " flowing")
            elif t.planet == "Saturn":
                effect = "Discipline & karma"
            elif t.planet == "Jupiter":
                effect = "Expansion & luck"
            elif t.planet == "Mars":
                effect = "Energy & drive"
            elif t.planet == "Venus":
                effect = "Love & pleasure"
            elif t.planet == "Mercury":
                effect = "Communication" + (" disrupted" if t.is_retrograde else " clear")
            else:
                effect = f"Influencing {t.house_from_moon}th house"

            transit_list.append(TransitInfo(
                planet=t.planet,
                status="Retrograde" if t.is_retrograde else "Direct",
                sign=t.sign,
                house=t.house_from_moon,
                effect=effect,
            ))

        remedy = None
        if battery.percentage < 40:
            remedy = "Light a ghee diya tonight and chant 'Om' 11 times. Your Moon energy needs grounding."

        return BatteryResponse(
            percentage=battery.percentage,
            level=battery.level,
            message=battery.message,
            detailed_reason="\n".join(battery.factors),
            active_transits=transit_list,
            remedy=remedy,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Battery error: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 5: ROAST
# POST /api/roast
# ═══════════════════════════════════════════════════════════════

@app.post("/api/roast", response_model=RoastResponse)
async def roast_sign(req: RoastRequest):
    try:
        user_dob = date(2000, 1, 1)
        if req.user_id:
            user = get_user(req.user_id)
            if user:
                user_dob = date.fromisoformat(user["dob"])

        planetary_context = format_planetary_context(req.sign.value, user_dob)

        roast = await generate_roast(
            sign=req.sign.value,
            planetary_context=planetary_context,
            context=req.context,
        )

        return RoastResponse(
            roast=roast,
            planetary_context=f"Current transits adding extra spice to {req.sign.value.capitalize()}'s energy",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roast machine broke: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 6: REMEDY / UPAY
# POST /api/remedy
# ═══════════════════════════════════════════════════════════════

@app.post("/api/remedy", response_model=RemedyResponse)
async def get_remedy(req: RemedyRequest):
    try:
        user = _require_user(req.user_id)
        user_dob = date.fromisoformat(user["dob"])
        planetary_context = format_planetary_context(req.sign.value, user_dob)

        result = await generate_remedy(
            sign=req.sign.value,
            planetary_context=planetary_context,
            concern=req.concern,
        )

        return RemedyResponse(
            title=result.get("title", "Daily Upay"),
            description=result.get("description", ""),
            icon=result.get("icon", "🪔"),
            for_concern=result.get("for_concern", "general"),
            planetary_basis=result.get("planetary_basis", ""),
            timing=result.get("timing", "Today"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remedy error: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 7: USER REGISTRATION
# POST /api/user
# ═══════════════════════════════════════════════════════════════

@app.post("/api/user")
async def create_user_route(req: UserCreate):
    try:
        user = create_user(
            name=req.name,
            sign=req.sign.value,
            dob=req.dob.isoformat(),
            birth_time=req.birth_time.isoformat() if req.birth_time else None,
            birth_place=req.birth_place,
        )

        return {
            "id": user["id"],
            "name": user["name"],
            "sign": user["sign"],
            "dob": user["dob"],
            "is_premium": bool(user["is_premium"]),
            "message": f"Welcome to Aura, {user['name']}! Your cosmic journey begins now ✦",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ROUTE 8: PAYMENTS (Razorpay)
# POST /api/payments/create-order
# POST /api/payments/verify
# ═══════════════════════════════════════════════════════════════

async def _razorpay_create_order(amount: int, currency: str = "INR") -> dict:
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay not configured")

    url = "https://api.razorpay.com/v1/orders"
    payload = {
        "amount": amount,
        "currency": currency,
        "payment_capture": 1,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), json=payload)

    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Razorpay error: {resp.text}")

    return resp.json()


@app.post("/api/payments/create-order", response_model=CreateOrderResponse)
async def create_payment_order(req: CreateOrderRequest):
    _require_user(req.user_id)

    price_table = {
        "receipts_single": 2900,
        "deep_dive_report": 4900,
        "instant_upay": 1100,
        "inner_circle": 19900,
    }
    amount = price_table.get(req.item, req.amount)

    order = await _razorpay_create_order(amount)

    internal_order_id = create_order(
        user_id=req.user_id,
        item=req.item,
        amount=order.get("amount", amount),
        currency=order.get("currency", "INR"),
        razorpay_order_id=order["id"],
    )

    return CreateOrderResponse(
        order_id=internal_order_id,
        amount=order.get("amount", amount),
        currency=order.get("currency", "INR"),
        razorpay_order_id=order["id"],
    )


@app.post("/api/payments/verify")
async def verify_payment(req: VerifyPaymentRequest):
    if not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay not configured")

    body = f"{req.razorpay_order_id}|{req.razorpay_payment_id}"
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, req.razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    order = get_order_by_razorpay_id(req.razorpay_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    mark_order_paid(order["order_id"], req.razorpay_payment_id)

    if order["item"] == "inner_circle":
        set_user_premium(order["user_id"], True)
    elif order["item"] == "receipts_single":
        add_receipts_credit(order["user_id"], 1)

    return {"status": "verified", "message": "Payment verified. Feature unlocked! ✦"}


# ═══════════════════════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ═══════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    init_db(settings.DB_PATH)
    print("✦ Aura AI Backend starting...")
    print(f"  Gemini Flash: {settings.GEMINI_MODEL_FLASH}")
    print(f"  Gemini Pro:   {settings.GEMINI_MODEL_PRO}")
    print(f"  API Key:      {'configured' if settings.GEMINI_API_KEY else 'MISSING!'}")
    print(f"  DB Path:      {settings.DB_PATH}")
    print("✦ The cosmos is online.")


@app.on_event("shutdown")
async def shutdown():
    print("✦ Aura AI Backend shutting down. The stars remain.")
