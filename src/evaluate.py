"""T10: shared scoring for the baseline and later models."""

import pandas as pd

from src.metrics import mae, wape

KG_FAMILIES = {"POULTRY", "MEATS", "PRODUCE"}
MIXED_FAMILIES = {"PREPARED FOODS", "FROZEN FOODS"}


def unit_type(family):
    """Return kg, mixed or count for one family name."""
    if family in KG_FAMILIES:
        return "kg"
    if family in MIXED_FAMILIES:
        return "mixed"
    return "count"


def eligible_rows(data):
    """T9 scoring rule: drop rows with missing lag_7 or flagged fill_after_last_train."""
    keep = data["lag_7"].notna() & ~data["fill_after_last_train"]
    return data.loc[keep].copy()


def score_period(scored, name):
    """Per-family MAE and WAPE, plus COUNT_OVERALL on count families.
    scored needs the columns family, target and prediction."""
    if scored.empty:
        raise ValueError(f"No eligible rows in {name}")
    if scored["target"].isna().any():
        raise ValueError(f"Missing target values in {name}")

    results = []
    for family, group in scored.groupby("family", observed=True):
        # same spelling as the families in the metrics CSV
        family = str(family).strip().upper()
        results.append({
            "period": name,
            "family": family,
            "unit_type": unit_type(family),
            "rows": len(group),
            "MAE": mae(group["target"], group["prediction"]),
            "WAPE_percent": wape(group["target"], group["prediction"]),
        })

    # kg and mixed units can't be added to counts, so the overall uses count families only
    count_rows = scored.loc[
        ~scored["family"].astype(str).str.strip().str.upper().isin(
            KG_FAMILIES | MIXED_FAMILIES
        )
    ]
    if count_rows.empty:
        raise ValueError(f"No count-family rows in {name}")

    results.append({
        "period": name,
        "family": "COUNT_OVERALL",
        "unit_type": "count",
        "rows": len(count_rows),
        "MAE": mae(count_rows["target"], count_rows["prediction"]),
        "WAPE_percent": wape(count_rows["target"], count_rows["prediction"]),
    })

    return pd.DataFrame(results)
