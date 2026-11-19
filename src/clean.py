"""T7 cleaning: sales_sample_v1 -> sales_clean_v1 + quarantine. (Issue #23)

Input : SALES_SAMPLE (never modified).
Output: SALES_CLEAN (good rows) and SALES_QUARANTINE (bad rows + 'reason').
All paths come from src/config.py.

Run from the repo root:  python -m src.clean              (refuses to overwrite)
                         python -m src.clean --overwrite
"""
import argparse
import os
import time

import pandas as pd

from src.config import SALES_SAMPLE, SALES_CLEAN, SALES_QUARANTINE
from src.subsample import WIN_START, WIN_END      # same window as T4, one source


def find_bad_rows(df):
    """Leen: duplicate, null and type checks.
    Returns (bad_rows with 'reason' column, good_df)."""
    raise NotImplementedError  # Leen fills this in


def check_dates(df):
    """Ali: date parsing + window check.
    Returns (bad_rows with 'reason' column, good_df)."""
    parsed = pd.to_datetime(df["date"], errors="coerce")   # broken date -> NaT
    bad_date = parsed.isna()
    outside = ~bad_date & ((parsed < WIN_START) | (parsed > WIN_END))
    is_bad = bad_date | outside

    bad = df[is_bad].copy()
    bad["reason"] = "outside_window"
    bad.loc[bad_date[is_bad], "reason"] = "bad_date"

    good = df[~is_bad].copy()
    good["date"] = parsed[~is_bad]
    return bad, good


def summarize(rows_in, clean, quarantine, seconds):                  # NEW
    """Markdown table for the PR description."""
    by_reason = quarantine["reason"].value_counts().to_dict() if len(quarantine) else {}
    ok = rows_in == len(clean) + len(quarantine)
    return f"""| Metric | Value |
|---|---|
| Rows in | {rows_in:,} |
| Rows out (clean) | {len(clean):,} |
| Quarantined | {len(quarantine):,} |
| Quarantined by reason | {by_reason or "none"} |
| rows_in = rows_out + quarantined | {"PASS" if ok else "FAIL"} |
| Clean dates | {clean['date'].min().date()} -> {clean['date'].max().date()} |
| Time | {seconds:.0f} s |"""


def main(overwrite=False):
    # ---- step 1: safety checks (same pattern as subsample.py)
    if not os.path.exists(SALES_SAMPLE):
        raise FileNotFoundError(f"{SALES_SAMPLE} not found. Is Drive mounted? Did T4 run?")
    out_dir = os.path.dirname(SALES_CLEAN)
    if not os.path.isdir(out_dir):
        raise FileNotFoundError("restockai-work/interim not found. Is Drive mounted?")
    for path in (SALES_CLEAN, SALES_QUARANTINE):
        if os.path.exists(path) and not overwrite:
            raise FileExistsError(f"{path} already exists. v1 is not overwritten "
                                  "silently: delete it on purpose or use --overwrite.")
    t0 = time.time()
    input_mtime = os.path.getmtime(SALES_SAMPLE)                      # NEW

    # ---- step 2: load (read only, the input file is never changed)
    df = pd.read_parquet(SALES_SAMPLE)
    rows_in = len(df)
    print(f"loaded: {rows_in:,} rows, columns = {list(df.columns)}")

    # ---- step 3 + 4: date parsing + window check
    bad_dates, df = check_dates(df)
    n_bad = (bad_dates["reason"] == "bad_date").sum()
    n_out = (bad_dates["reason"] == "outside_window").sum()
    print(f"date check: {n_bad:,} bad dates, {n_out:,} outside "
          f"{WIN_START.date()} -> {WIN_END.date()}")

    # ---- step 5: Leen's checks (added when find_bad_rows is ready)  # NEW
    bad_parts = [bad_dates]

    # ---- step 6: count check, then save                             # NEW
    quarantine = pd.concat(bad_parts, ignore_index=True)
    if rows_in != len(df) + len(quarantine):
        raise RuntimeError(f"rows lost: {rows_in:,} in, {len(df):,} out, "
                           f"{len(quarantine):,} quarantined. Nothing was saved.")
    df.to_parquet(SALES_CLEAN, index=False)
    quarantine.to_parquet(SALES_QUARANTINE, index=False)   # written even with 0 rows
    if os.path.getmtime(SALES_SAMPLE) != input_mtime:
        raise RuntimeError(f"{SALES_SAMPLE} was modified. It must never change.")
    print(f"saved: {SALES_CLEAN} ({os.path.getsize(SALES_CLEAN) / 1e6:.1f} MB)")
    print(f"saved: {SALES_QUARANTINE} ({len(quarantine):,} rows)")

    # ---- step 7: summary                                             # NEW
    print("\nSUMMARY (paste in the PR)")
    print(summarize(rows_in, df, quarantine, time.time() - t0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T7: build sales_clean_v1.parquet")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace existing sales_clean_v1 / sales_quarantine_v1")
    main(overwrite=parser.parse_args().overwrite)
