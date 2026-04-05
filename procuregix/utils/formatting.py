from __future__ import annotations

import zlib
from datetime import datetime

import pandas as pd

from procuregix.config import NEED_ATTENTION_STATUSES


def line_total(row) -> float:
    return float(row["quantity"]) * float(row["unit_price"])


def parse_created_display(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return iso_str


def stable_key(s: str, prefix: str) -> str:
    h = zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF
    return f"{prefix}_{h:x}"


def student_status_label(raw: str) -> str:
    key = (raw or "").strip().lower()
    labels = {
        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
        "ordered": "Ordered",
        "received": "Arrived",
        "archived": "Archived",
        "backordered": "Backordered",
        "returned_refunded": "Returned / Refunded",
        "arrived": "Arrived",
        "needs_return": "Needs return",
        "verified": "Verified",
        "cancelled": "Cancelled",
    }
    if key in labels:
        return labels[key]
    return (raw or "").replace("_", " ").strip().title() or "—"


def attention_text_for_student(row: dict) -> str:
    msg = (row.get("attention_message") or "")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    notes = row.get("notes") or ""
    if isinstance(notes, str) and notes.strip():
        return f"(Your notes) {notes.strip()}"
    return "—"


def notification_body_for_student(row: dict) -> str:
    """Human-readable line for the notifications panel when there is no custom message."""
    raw = attention_text_for_student(row)
    if raw != "—":
        return raw
    stl = str(row.get("status", "")).lower()
    hints = {
        "backordered": "This item is backordered — it may be delayed or not in stock yet. Check with your instructor.",
        "rejected": "This request was rejected — review the feedback and resubmit if appropriate.",
        "returned_refunded": "This line was returned or refunded — follow up if you still need the item.",
    }
    return hints.get(stl, "Please review this order line.")


def student_orders_for_notifications(mine: pd.DataFrame) -> pd.DataFrame:
    if mine.empty:
        return mine
    ms = mine["status"].astype(str).str.lower()
    if "attention_message" in mine.columns:
        am = mine["attention_message"].fillna("").astype(str).str.strip()
        mask = ms.isin(NEED_ATTENTION_STATUSES) | (am != "")
    else:
        mask = ms.isin(NEED_ATTENTION_STATUSES)
    return mine.loc[mask].copy()
