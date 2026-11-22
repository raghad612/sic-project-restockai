"""T8 - Features v1: sales_clean_v1 -> features_v1. (Issue #28)

Input : SALES_CLEAN (never modified), HOLIDAYS_OUT, STORES_OUT.
Output: FEATURES (restockai-work/processed/features_v1.parquet), same rows as the input.
All paths come from src/config.py.

Rules (Issue #28):
- target = unit_sales with negatives set to 0.
- Lags and rolling means go by DATE, never by row position, and never use today's value.
- No statistic is fitted on dates after 2017-04-30 (TRAIN_END). Features cover all dates.
- Holiday flags follow the T6 encoding list (notebooks/02_eda_promo_holidays_raghad.ipynb).

Run from the repo root:  python -m src.features              (refuses to overwrite)
                         python -m src.features --overwrite
"""
import argparse
import os
import time

import numpy as np
import pandas as pd

from src.config import SALES_CLEAN, HOLIDAYS_OUT, STORES_OUT, FEATURES
from src.subsample import TRAIN_END                 # 2017-04-30, same split as T4, one source
from src.clean import QUAKE_START, QUAKE_END        # same quake window as T7, one source

# the functions only need these columns, so they run on the sample and the clean file
REQUIRED_COLS = ["date", "store_nbr", "item_nbr", "unit_sales", "onpromotion"]
KEYS = ["date", "store_nbr", "item_nbr"]
SERIES = ["store_nbr", "item_nbr"]                 # one time series per store-item
LAGS = [1, 7, 14]
WINDOWS = [7, 28]


# ---------------------------------------------------------------- feature groups
def add_target(df):
    """target = unit_sales with negatives (returns) set to 0: demand is never negative."""
    df = df.copy()
    df["target"] = df["unit_sales"].clip(lower=0)
    return df


def add_calendar(df):
    """Calendar features from the date only (no future information needed)."""
    df = df.copy()
    d = df["date"].dt
    df["weekday"] = d.dayofweek.astype("int8")                 # 0 = Monday ... 6 = Sunday
    df["day_of_month"] = d.day.astype("int8")                  # 1 ... 31
    df["month"] = d.month.astype("int8")                       # 1 ... 12
    df["week_of_year"] = d.isocalendar().week.astype("int8")   # 1 ... 53 (ISO)
    return df


def add_quake(df):
    """quake_period for 2016-04-16 to 2016-04-30. T7 already creates it on the clean
    file, so it is only added when missing (for example on the sample)."""
    if "quake_period" not in df.columns:
        df = df.copy()
        df["quake_period"] = df["date"].between(QUAKE_START, QUAKE_END)
    return df


def add_holidays(df, holidays, stores):
    """T6 rules: celebrated days only (no Event, no Work Day, no transferred=True row:
    the Transfer row is the real day). Built from type, locale and locale_name, never
    from holiday names. No regional flag in v1 (0 store-days in our 12 stores).
    One record per date (national) and per store-date (local) before merging,
    so the merge can never duplicate sales rows."""
    celebrated = holidays[(holidays["transferred"] == False)
                          & (~holidays["type"].isin(["Event", "Work Day"]))]

    # national: same for all stores; two flags because their effects differ (+10% vs +38%)
    national = celebrated[celebrated["locale"] == "National"].copy()
    national["hol_national_dayoff"] = national["type"].isin(["Holiday", "Transfer"]).astype("int8")
    national["hol_national_shopping"] = national["type"].isin(["Additional", "Bridge"]).astype("int8")
    national = national.groupby("date", as_index=False)[
        ["hol_national_dayoff", "hol_national_shopping"]].max()

    # local: matched on the store's city
    local = celebrated[celebrated["locale"] == "Local"][["date", "locale_name"]]
    local = local.merge(stores[["store_nbr", "city"]], left_on="locale_name", right_on="city")
    local = local[local["store_nbr"].isin(df["store_nbr"].unique())]
    local = local[["store_nbr", "date"]].drop_duplicates()
    local["store_nbr"] = local["store_nbr"].astype(df["store_nbr"].dtype)
    local["hol_local"] = 1

    flags = ["hol_national_dayoff", "hol_national_shopping", "hol_local"]
    df = df.drop(columns=flags, errors="ignore")
    df = df.merge(national, on="date", how="left", validate="many_to_one")
    df = df.merge(local, on=["store_nbr", "date"], how="left", validate="many_to_one")
    df[flags] = df[flags].fillna(0).astype("int8")
    return df


def add_lag(df, k):
    """lag_k = target of the same store-item k days earlier, by date (not by row):
    shift a copy's date forward by k days and merge it back. A missing day gives NaN."""
    col = f"lag_{k}"
    df = df.drop(columns=[col], errors="ignore")
    s = df[KEYS + ["target"]].copy()
    s["date"] = s["date"] + pd.Timedelta(days=k)
    s = s.rename(columns={"target": col})
    return df.merge(s, on=KEYS, how="left", validate="one_to_one")


def add_rolling(df, w):
    """roll_mean_w = mean target of the previous w calendar days, today excluded
    (closed="left": window [date - w days, date)). Missing days are simply not in the mean."""
    col = f"roll_mean_{w}"
    df = df.drop(columns=[col], errors="ignore")
    # groupby returns rows ordered by store, item, date: sort df the same way to realign
    df = df.sort_values(SERIES + ["date"]).reset_index(drop=True)
    r = (df.groupby(SERIES)
           .rolling(f"{w}D", on="date", closed="left")["target"]
           .mean())
    assert len(r) == len(df), "rolling result has a different length"
    df[col] = r.to_numpy()
    return df


def add_fill_after_last_train(df):
    """Step 9b: True for filled zeros up to TRAIN_END that come after the store-item's
    last real row up to TRAIN_END. T7 created them only because the item sold again
    after the split (future information). Rows are kept; the ML phase skips them."""
    df = df.drop(columns=["fill_after_last_train"], errors="ignore")
    if "is_filled" not in df.columns:              # e.g. the sample: nothing was filled
        df["fill_after_last_train"] = False
        return df
    real = df[(~df["is_filled"]) & (df["date"] <= TRAIN_END)]
    last_real = (real.groupby(SERIES, as_index=False)["date"].max()
                     .rename(columns={"date": "_last_real"}))
    df = df.merge(last_real, on=SERIES, how="left", validate="many_to_one")
    flag = df["is_filled"] & (df["date"] <= TRAIN_END) & (df["date"] > df["_last_real"])
    df["fill_after_last_train"] = flag.fillna(False).astype(bool)
    return df.drop(columns=["_last_real"])


def encode_promo(df):
    """Step 10: onpromotion -> float32 (1 promo, 0 no promo). Missing (filled rows)
    stays NaN: LightGBM handles it, and filling with 0 would invent 'no promotion'."""
    df = df.copy()
    if df["onpromotion"].dtype != "float32":
        df["onpromotion"] = (df["onpromotion"].astype("Float32")
                             .to_numpy(dtype="float32", na_value=np.nan))
    return df


def build_features(sales, holidays, stores):
    """All feature groups in order. Needs only date, store_nbr, item_nbr, unit_sales,
    onpromotion (+ is_filled when present), so it runs on the sample and the clean file."""
    df = add_target(sales)
    df = add_calendar(df)
    df = add_quake(df)
    df = add_holidays(df, holidays, stores)
    for k in LAGS:
        df = add_lag(df, k)
    for w in WINDOWS:
        df = add_rolling(df, w)
    df = add_fill_after_last_train(df)
    df = encode_promo(df)
    return df.sort_values(KEYS).reset_index(drop=True)


# ---------------------------------------------------------------- checks
def check_features(sales, df):
    """Stop with an error if a rule is broken. Returns the missing-value table."""
    assert len(df) == len(sales), f"row count changed: {len(sales)} -> {len(df)}"
    assert not df.duplicated(KEYS).any(), "duplicate (date, store, item) rows"
    assert (df["target"] >= 0).all(), "negative target"
    flags = ["hol_national_dayoff", "hol_national_shopping", "hol_local"]
    assert df[flags].notna().all().all(), "null holiday flag"
    f = df["fill_after_last_train"]
    assert f.notna().all(), "null fill_after_last_train"
    assert not (f & (df["date"] > TRAIN_END)).any(), "flagged row after TRAIN_END"
    missing = df.isna().sum()
    return missing[missing > 0]


def summarize(df, missing, seconds):
    """Markdown table for the PR description."""
    rows = "\n".join(f"| {c} missing | {n:,} |" for c, n in missing.items())
    return f"""| Metric | Value |
|---|---|
| Rows | {len(df):,} |
| Columns | {df.shape[1]} |
| First date | {df['date'].min().date()} |
| Last date | {df['date'].max().date()} |
| target zeros | {int((df['target'] == 0).sum()):,} |
| hol_national_dayoff rows | {int(df['hol_national_dayoff'].sum()):,} |
| hol_national_shopping rows | {int(df['hol_national_shopping'].sum()):,} |
| hol_local rows | {int(df['hol_local'].sum()):,} |
| fill_after_last_train rows | {int(df['fill_after_last_train'].sum()):,} |
{rows}
| Run time | {seconds:.0f} s |"""


# ---------------------------------------------------------------- main
def main(overwrite=False):
    # ---- step 1: safety checks (same pattern as subsample.py and clean.py)
    for path in (SALES_CLEAN, HOLIDAYS_OUT, STORES_OUT):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} not found. Is Drive mounted? Did T4/T7 run?")
    out_dir = os.path.dirname(FEATURES)
    if not os.path.isdir(out_dir):
        raise FileNotFoundError("restockai-work/processed not found. Is Drive mounted?")
    if os.path.exists(FEATURES) and not overwrite:
        raise FileExistsError(f"{FEATURES} already exists. v1 is not overwritten "
                              "silently: delete it on purpose or use --overwrite.")
    t0 = time.time()
    input_mtime = os.path.getmtime(SALES_CLEAN)

    # ---- step 2: load (read only, the input files are never changed)
    sales = pd.read_parquet(SALES_CLEAN)
    holidays = pd.read_parquet(HOLIDAYS_OUT)
    stores = pd.read_parquet(STORES_OUT)
    print(f"loaded: {len(sales):,} rows, columns = {list(sales.columns)}")
    missing_cols = [c for c in REQUIRED_COLS if c not in sales.columns]
    if missing_cols:
        raise KeyError(f"missing required columns: {missing_cols}")

    # ---- step 3: build features, then stop if any rule is broken (nothing saved)
    df = build_features(sales, holidays, stores)
    missing = check_features(sales, df)
    print("checks: PASS")

    # ---- step 4: save
    df.to_parquet(FEATURES, index=False)
    if os.path.getmtime(SALES_CLEAN) != input_mtime:
        raise RuntimeError(f"{SALES_CLEAN} was modified. It must never change.")
    print(f"saved: {FEATURES} ({os.path.getsize(FEATURES) / 1e6:.1f} MB)")
    print("\nSUMMARY (paste in the PR)")
    print(summarize(df, missing, time.time() - t0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T8: build features_v1.parquet")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace an existing features_v1.parquet")
    main(overwrite=parser.parse_args().overwrite)
