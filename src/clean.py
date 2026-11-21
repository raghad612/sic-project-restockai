
"""T7 cleaning: sales_sample_v1 -> sales_clean_v1 + quarantine. (Issue #23)

Input : SALES_SAMPLE (never modified).
Output: SALES_CLEAN (good rows + zero-filled rows + flags) and
        SALES_QUARANTINE (bad rows + 'reason').
All paths come from src/config.py.

Run from the repo root:  python -m src.clean              (refuses to overwrite)
                         python -m src.clean --overwrite
"""
import argparse
import os
import time

import numpy as np
import pandas as pd

from src.config import SALES_SAMPLE, SALES_CLEAN, SALES_QUARANTINE
from src.subsample import WIN_START, WIN_END      # same window as T4, one source


# schema: a missing column or wrong type is a file problem, not a row problem -> error
REQUIRED_COLS = ["date", "store_nbr", "item_nbr", "unit_sales",
                 "onpromotion", "family", "class", "perishable"]
KEY_COLS = ["date", "store_nbr", "item_nbr"]
NUMERIC_COLS = ["store_nbr", "item_nbr", "unit_sales"]

# Part 2 rules (Issue #23, decisions by Leen, answers by Raghad)
QUAKE_START = pd.Timestamp("2016-04-16")          # earthquake period: kept and flagged
QUAKE_END = pd.Timestamp("2016-04-30")
# dates with no sales in any store (T5): likely closures (not verified) -> never zero-filled
CLOSED_DATES = pd.to_datetime(["2015-12-25", "2016-01-01", "2016-12-25", "2017-01-01"])


def find_bad_rows(df):
    """Leen: schema check, null checks, duplicate check.
    Returns (bad_rows with 'reason' column, good_df). Input df is not changed.

    Reasons: null_<column> (key columns + unit_sales), duplicate (extra copies of a
    (date, store, item); the first copy stays). A row with several problems is listed
    once, reasons joined with ';'. Negative unit_sales are NOT bad (returns, flagged later).
    """
    # ---- schema (raise, do not quarantine)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}. Found: {list(df.columns)}")
    wrong = [c for c in NUMERIC_COLS if not pd.api.types.is_numeric_dtype(df[c])]
    if wrong:
        raise TypeError(f"columns must be numeric: {wrong}. "
                        f"Got: { {c: str(df[c].dtype) for c in wrong} }")

    # ---- one boolean mask per check (numpy, so a repeated index cannot break it)
    checks = {f"null_{c}": df[c].isna().to_numpy() for c in KEY_COLS + ["unit_sales"]}
    keys_ok = ~(checks["null_date"] | checks["null_store_nbr"] | checks["null_item_nbr"])
    # why keys_ok: rows with a null key are not compared, NaN == NaN would fake duplicates
    checks["duplicate"] = df.duplicated(KEY_COLS, keep="first").to_numpy() & keys_ok

    # ---- one reason string per row, all failed checks joined
    reason = np.full(len(df), "", dtype=object)
    for name, mask in checks.items():
        reason[mask] = np.where(reason[mask] == "", name, reason[mask] + ";" + name)
    is_bad = reason != ""

    bad = df[is_bad].copy()
    bad["reason"] = reason[is_bad]
    return bad, df[~is_bad].copy()


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


def zero_fill(df):
    """Ali: add unit_sales = 0 rows for missing days inside each store-item's
    active period (first row to last row), never before/after, never on CLOSED_DATES.
    Filled rows: family/class/perishable copied from the item, onpromotion = <NA>
    (T8 decides how to encode it), is_filled = True.
    Returns (df with filled rows added, number of filled rows)."""
    keys = ["store_nbr", "item_nbr"]
    span = df.groupby(keys)["date"].agg(first="min", last="max").reset_index()
    n_days = (span["last"] - span["first"]).dt.days + 1

    # every day of every active period
    grid = span.loc[span.index.repeat(n_days), keys + ["first"]]
    offset = grid.groupby(level=0).cumcount()
    grid["date"] = grid["first"] + pd.to_timedelta(offset.to_numpy(), unit="D")
    grid = grid.drop(columns="first")
    grid = grid[~grid["date"].isin(CLOSED_DATES)]

    # keep only the days that have no row yet
    have = df[keys + ["date"]].assign(_have=True)
    grid = grid.merge(have, on=keys + ["date"], how="left")
    filled = grid[grid["_have"].isna()].drop(columns="_have")

    # item info copied from the item's own rows
    item_info = df.drop_duplicates("item_nbr")[["item_nbr", "family", "class", "perishable"]]
    filled = filled.merge(item_info, on="item_nbr", how="left", validate="many_to_one")
    filled["unit_sales"] = np.float32(0)
    filled["onpromotion"] = pd.array([pd.NA] * len(filled), dtype="boolean")
    filled["is_filled"] = True

    out = df.assign(is_filled=False)
    out = pd.concat([out, filled[out.columns]], ignore_index=True)
    out = out.astype(df.dtypes.to_dict())          # same types as the input columns
    out = out.sort_values(KEY_COLS).reset_index(drop=True)
    return out, len(filled)


def add_flags(df):
    """Ali: is_return (negative unit_sales, kept as recorded) and quake_period."""
    df = df.copy()
    df["is_return"] = df["unit_sales"] < 0
    df["quake_period"] = df["date"].between(QUAKE_START, QUAKE_END)
    return df


def summarize(rows_in, n_filled, clean, quarantine, seconds):
    """Markdown table for the PR description."""
    by_reason = quarantine["reason"].value_counts().to_dict() if len(quarantine) else {}
    ok = rows_in + n_filled == len(clean) + len(quarantine)
    return f"""| Metric | Value |
|---|---|
| Rows in | {rows_in:,} |
| Zero-filled rows added | {n_filled:,} |
| Rows out (clean) | {len(clean):,} |
| Quarantined | {len(quarantine):,} |
| Quarantined by reason | {by_reason or "none"} |
| rows_in + filled = rows_out + quarantined | {"PASS" if ok else "FAIL"} |
| is_return rows | {int(clean['is_return'].sum()):,} |
| quake_period rows | {int(clean['quake_period'].sum()):,} |
| Rows on closure dates | {int(clean['date'].isin(CLOSED_DATES).sum()):,} |
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
    input_mtime = os.path.getmtime(SALES_SAMPLE)

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

    # ---- step 5: Leen's checks: schema, nulls, duplicates
    bad_other, df = find_bad_rows(df)
    print(f"null/duplicate check: {len(bad_other):,} rows quarantined "
          f"{bad_other['reason'].value_counts().to_dict() if len(bad_other) else ''}")
    bad_parts = [bad_dates, bad_other]

    # ---- step 6: zero-fill inside active periods, then flags (Part 2)
    df, n_filled = zero_fill(df)
    df = add_flags(df)
    print(f"zero-fill: {n_filled:,} rows added (closure dates skipped: "
          f"{[str(d.date()) for d in CLOSED_DATES]})")

    # ---- step 7: count check, then save
    quarantine = pd.concat(bad_parts, ignore_index=True)
    if rows_in + n_filled != len(df) + len(quarantine):
        raise RuntimeError(f"rows lost: {rows_in:,} in + {n_filled:,} filled, "
                           f"{len(df):,} out, {len(quarantine):,} quarantined. "
                           "Nothing was saved.")
    df.to_parquet(SALES_CLEAN, index=False)
    quarantine.to_parquet(SALES_QUARANTINE, index=False)   # written even with 0 rows
    if os.path.getmtime(SALES_SAMPLE) != input_mtime:
        raise RuntimeError(f"{SALES_SAMPLE} was modified. It must never change.")
    print(f"saved: {SALES_CLEAN} ({os.path.getsize(SALES_CLEAN) / 1e6:.1f} MB)")
    print(f"saved: {SALES_QUARANTINE} ({len(quarantine):,} rows)")

    # ---- step 8: summary
    print("\nSUMMARY (paste in the PR)")
    print(summarize(rows_in, n_filled, df, quarantine, time.time() - t0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T7: build sales_clean_v1.parquet")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace existing sales_clean_v1 / sales_quarantine_v1")
    main(overwrite=parser.parse_args().overwrite)
