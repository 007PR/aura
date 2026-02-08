# storage.py — Storage layer for Aura AI (SQLite or Supabase)

import sqlite3
from pathlib import Path
from datetime import datetime, date
import uuid
from typing import Optional, Dict, Any

from config import settings

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

_DB_PATH: Optional[Path] = None
_SUPABASE = None
_USE_SUPABASE = False


def init_db(db_path: str) -> None:
    """Initialize storage backend (Supabase or SQLite)."""
    global _DB_PATH, _SUPABASE, _USE_SUPABASE

    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        if not SUPABASE_AVAILABLE:
            raise RuntimeError("Supabase client not installed. Install 'supabase' dependency.")
        _SUPABASE = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        _USE_SUPABASE = True
        return

    _USE_SUPABASE = False
    _DB_PATH = Path(db_path)
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sign TEXT NOT NULL,
                dob TEXT NOT NULL,
                birth_time TEXT,
                birth_place TEXT,
                created_at TEXT NOT NULL,
                is_premium INTEGER NOT NULL DEFAULT 0,
                messages_today INTEGER NOT NULL DEFAULT 0,
                messages_date TEXT NOT NULL,
                receipts_today INTEGER NOT NULL DEFAULT 0,
                receipts_date TEXT NOT NULL,
                receipts_credits INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                item TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                razorpay_order_id TEXT NOT NULL,
                razorpay_payment_id TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_rzp ON orders(razorpay_order_id)")
        conn.commit()


def _connect() -> sqlite3.Connection:
    if _DB_PATH is None:
        raise RuntimeError("Database not initialized")
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _today_str() -> str:
    return date.today().isoformat()


def _normalize_user(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row)
    row["messages_today"] = int(row.get("messages_today") or 0)
    row["receipts_today"] = int(row.get("receipts_today") or 0)
    row["receipts_credits"] = int(row.get("receipts_credits") or 0)
    return row


def _sb_table(name: str):
    if not _SUPABASE:
        raise RuntimeError("Supabase client not initialized")
    return _SUPABASE.table(name)


def _sb_get_user(user_id: str) -> Optional[Dict[str, Any]]:
    resp = _sb_table("users").select("*").eq("id", user_id).limit(1).execute()
    data = getattr(resp, "data", None) or []
    if not data:
        return None
    return _normalize_user(data[0])


def _sb_update_user(user_id: str, updates: Dict[str, Any]) -> None:
    _sb_table("users").update(updates).eq("id", user_id).execute()


def _sb_reset_daily_counts(user: Dict[str, Any]) -> Dict[str, Any]:
    today = _today_str()
    updates = {}

    if user.get("messages_date") != today:
        updates["messages_today"] = 0
        updates["messages_date"] = today

    if user.get("receipts_date") != today:
        updates["receipts_today"] = 0
        updates["receipts_date"] = today

    if updates:
        _sb_update_user(user["id"], updates)
        user = _sb_get_user(user["id"]) or user

    return user


def create_user(
    name: str,
    sign: str,
    dob: str,
    birth_time: Optional[str] = None,
    birth_place: Optional[str] = None,
) -> Dict[str, Any]:
    user_id = "user_" + uuid.uuid4().hex[:12]
    created_at = datetime.utcnow().isoformat()
    today = _today_str()

    if _USE_SUPABASE:
        payload = {
            "id": user_id,
            "name": name,
            "sign": sign,
            "dob": dob,
            "birth_time": birth_time,
            "birth_place": birth_place,
            "created_at": created_at,
            "is_premium": False,
            "messages_today": 0,
            "messages_date": today,
            "receipts_today": 0,
            "receipts_date": today,
            "receipts_credits": 0,
        }
        _sb_table("users").insert(payload).execute()
        return _sb_get_user(user_id)

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (
                id, name, sign, dob, birth_time, birth_place, created_at,
                is_premium, messages_today, messages_date, receipts_today,
                receipts_date, receipts_credits
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 0, ?, 0)
            """,
            (user_id, name, sign, dob, birth_time, birth_place, created_at, today, today)
        )
        conn.commit()

    return get_user(user_id)


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    if _USE_SUPABASE:
        user = _sb_get_user(user_id)
        if not user:
            return None
        return _sb_reset_daily_counts(user)

    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return None
        _reset_daily_counts_sqlite(conn, row)
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row)


def _reset_daily_counts_sqlite(conn: sqlite3.Connection, row: sqlite3.Row) -> None:
    today = _today_str()
    updates = []
    params = []

    if row["messages_date"] != today:
        updates.append("messages_today = 0")
        updates.append("messages_date = ?")
        params.append(today)

    if row["receipts_date"] != today:
        updates.append("receipts_today = 0")
        updates.append("receipts_date = ?")
        params.append(today)

    if updates:
        params.append(row["id"])
        conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()


def set_user_premium(user_id: str, is_premium: bool) -> None:
    if _USE_SUPABASE:
        _sb_update_user(user_id, {"is_premium": bool(is_premium)})
        return

    with _connect() as conn:
        conn.execute("UPDATE users SET is_premium = ? WHERE id = ?", (1 if is_premium else 0, user_id))
        conn.commit()


def increment_messages_today(user_id: str) -> None:
    if _USE_SUPABASE:
        user = _sb_get_user(user_id)
        if not user:
            return
        _sb_update_user(user_id, {"messages_today": int(user.get("messages_today") or 0) + 1})
        return

    with _connect() as conn:
        conn.execute("UPDATE users SET messages_today = messages_today + 1 WHERE id = ?", (user_id,))
        conn.commit()


def increment_receipts_today(user_id: str) -> None:
    if _USE_SUPABASE:
        user = _sb_get_user(user_id)
        if not user:
            return
        _sb_update_user(user_id, {"receipts_today": int(user.get("receipts_today") or 0) + 1})
        return

    with _connect() as conn:
        conn.execute("UPDATE users SET receipts_today = receipts_today + 1 WHERE id = ?", (user_id,))
        conn.commit()


def add_receipts_credit(user_id: str, credits: int) -> None:
    if _USE_SUPABASE:
        user = _sb_get_user(user_id)
        if not user:
            return
        _sb_update_user(user_id, {"receipts_credits": int(user.get("receipts_credits") or 0) + credits})
        return

    with _connect() as conn:
        conn.execute("UPDATE users SET receipts_credits = receipts_credits + ? WHERE id = ?", (credits, user_id))
        conn.commit()


def consume_receipts_credit(user_id: str) -> bool:
    if _USE_SUPABASE:
        user = _sb_get_user(user_id)
        if not user or int(user.get("receipts_credits") or 0) <= 0:
            return False
        _sb_update_user(user_id, {"receipts_credits": int(user.get("receipts_credits") or 0) - 1})
        return True

    with _connect() as conn:
        row = conn.execute("SELECT receipts_credits FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or row["receipts_credits"] <= 0:
            return False
        conn.execute("UPDATE users SET receipts_credits = receipts_credits - 1 WHERE id = ?", (user_id,))
        conn.commit()
        return True


def create_order(
    user_id: str,
    item: str,
    amount: int,
    currency: str,
    razorpay_order_id: str,
) -> str:
    order_id = "order_" + uuid.uuid4().hex[:12]
    created_at = datetime.utcnow().isoformat()

    if _USE_SUPABASE:
        payload = {
            "order_id": order_id,
            "user_id": user_id,
            "item": item,
            "amount": amount,
            "currency": currency,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": None,
            "status": "created",
            "created_at": created_at,
        }
        _sb_table("orders").insert(payload).execute()
        return order_id

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO orders (
                order_id, user_id, item, amount, currency,
                razorpay_order_id, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (order_id, user_id, item, amount, currency, razorpay_order_id, "created", created_at)
        )
        conn.commit()

    return order_id


def get_order_by_razorpay_id(razorpay_order_id: str) -> Optional[Dict[str, Any]]:
    if _USE_SUPABASE:
        resp = _sb_table("orders").select("*").eq("razorpay_order_id", razorpay_order_id).limit(1).execute()
        data = getattr(resp, "data", None) or []
        return data[0] if data else None

    with _connect() as conn:
        row = conn.execute("SELECT * FROM orders WHERE razorpay_order_id = ?", (razorpay_order_id,)).fetchone()
        return dict(row) if row else None


def mark_order_paid(order_id: str, razorpay_payment_id: str) -> None:
    if _USE_SUPABASE:
        _sb_table("orders").update({"status": "paid", "razorpay_payment_id": razorpay_payment_id}).eq("order_id", order_id).execute()
        return

    with _connect() as conn:
        conn.execute(
            "UPDATE orders SET status = ?, razorpay_payment_id = ? WHERE order_id = ?",
            ("paid", razorpay_payment_id, order_id)
        )
        conn.commit()
