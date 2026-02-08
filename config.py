# config.py — Environment configuration for Aura AI Backend

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _parse_cors(origins: str) -> list:
    if not origins:
        return ["*"]
    origins = origins.strip()
    if origins == "*":
        return ["*"]
    return [o.strip() for o in origins.split(",") if o.strip()]


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


class Settings:
    """Application settings loaded from environment variables."""

    # App
    APP_ENV: str = os.getenv("APP_ENV", "dev")

    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_FLASH: str = os.getenv("GEMINI_MODEL_FLASH", "gemini-1.5-flash")
    GEMINI_MODEL_PRO: str = os.getenv("GEMINI_MODEL_PRO", "gemini-1.5-pro")
    GEMINI_API_BASE: str = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta")

    # Database (Supabase PostgreSQL or local SQLite)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    DB_PATH: str = os.getenv("AURA_DB_PATH", str(Path(__file__).resolve().parent / "aura.db"))

    # Razorpay
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")

    # App settings
    FREE_MESSAGES_PER_DAY: int = _get_int("FREE_MESSAGES_PER_DAY", 3)
    FREE_RECEIPTS_PER_DAY: int = _get_int("FREE_RECEIPTS_PER_DAY", 0)
    CORS_ORIGINS: list = _parse_cors(os.getenv("CORS_ORIGINS", "*"))

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = _get_int("RATE_LIMIT_PER_MINUTE", 20)


settings = Settings()
