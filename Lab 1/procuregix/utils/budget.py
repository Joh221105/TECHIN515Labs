from __future__ import annotations

import pandas as pd


def approved_spend_by_class_for_cfo(mine: pd.DataFrame, class_names: list[str]) -> dict[str, float]:
    """Sum line totals (qty × unit price) for approved rows only, per class name."""
    out = {c: 0.0 for c in class_names}
    if mine.empty or "status" not in mine.columns or not class_names:
        return out
    ap = mine[mine["status"].astype(str).str.lower() == "approved"]
    for _, row in ap.iterrows():
        c = row["class_name"]
        if c in out:
            out[c] += float(row["quantity"]) * float(row["unit_price"])
    return out


def approved_spend_for_class_program_wide(df: pd.DataFrame, class_name: str) -> float:
    """Approved line-total sum for a class across all CFOs (teacher dashboard)."""
    if df.empty or "status" not in df.columns:
        return 0.0
    ap = df[
        (df["class_name"] == class_name)
        & (df["status"].astype(str).str.lower() == "approved")
    ]
    return float((ap["quantity"] * ap["unit_price"]).sum())


def order_line_count_for_class(df: pd.DataFrame, class_name: str) -> int:
    """Number of order line rows for a class."""
    if df.empty or "class_name" not in df.columns:
        return 0
    return int((df["class_name"] == class_name).sum())
