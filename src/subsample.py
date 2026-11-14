"""T4 - Build a small Favorita sample that runs on free Colab.

About 12 stores x 250 items over 24 whole months (2015-08-01 to 2017-07-31).

Input : train.csv, items.csv, stores.csv extracted to LOCAL (Colab local disk).
Output: SALES_SAMPLE (restockai-work/interim/sales_sample_v1.parquet).
All paths come from src/config.py.

train.csv is never loaded whole: it is read 3 times in chunks of 5,000,000 rows.
  pass (a) choose stores : rows in all 24 months, round-robin over types A-E by
                           training-part sales, at most 2 stores per city.
  pass (b) choose items  : training part only (<= 2017-04-30), chosen stores only;
                           sold (unit_sales > 0) in >= 80% of the 91 full weeks,
                           ranked by total unit_sales, >= 84 perishable,
                           >= 8 families, <= 62 items per family.
  pass (c) build sample  : chosen stores x items over the whole window, onpromotion
                           -> True/False/<NA>, join family/class/perishable, no id.

Not done here on purpose (left to T7/T8): filling missing zero-sales rows,
removing negative unit_sales (returns), filling blank onpromotion.

Run from the repo root:  python -m src.subsample          (refuses to overwrite)
                         python -m src.subsample --overwrite
"""
import argparse
import math
import os
import time

import pandas as pd

from src.config import LOCAL, SALES_SAMPLE

# ---------------------------------------------------------------- settings
TRAIN_CSV = os.path.join(LOCAL, "train.csv")
ITEMS_CSV = os.path.join(LOCAL, "items.csv")
STORES_CSV = os.path.join(LOCAL, "stores.csv")

CHUNK = 5_000_000                          # rows per chunk (tested by Raghad)

WIN_START = pd.Timestamp("2015-08-01")     # 24 whole months
WIN_END = pd.Timestamp("2017-07-31")       # Aug 2017 is partial -> left out
TRAIN_END = pd.Timestamp("2017-04-30")     # items/stores chosen on this part only

N_STORES = 12
MAX_PER_CITY = 2

N_ITEMS = 250
MIN_WEEK_SHARE = 0.80
MIN_PERISH = math.ceil(N_ITEMS / 3)        # 84
MIN_FAMILIES = 8
MAX_PER_FAMILY = N_ITEMS // 4              # 62

USECOLS = ["date", "store_nbr", "item_nbr", "unit_sales", "onpromotion"]   # no id
DTYPES = {"store_nbr": "int8", "item_nbr": "int32",
          "unit_sales": "float32", "onpromotion": "str"}


# ---------------------------------------------------------------- helpers
def read_chunks(cols):
    """Yield chunks of train.csv with only `cols`, small dtypes, parsed dates."""
    dtypes = {c: t for c, t in DTYPES.items() if c in cols}
    for ch in pd.read_csv(TRAIN_CSV, usecols=cols, dtype=dtypes, chunksize=CHUNK):
        ch["date"] = pd.to_datetime(ch["date"], format="%Y-%m-%d")
        yield ch


def to_bool_promo(s):
    """'True'->True, 'False'->False, blank-><NA>. Any other value -> error."""
    out = s.map({"True": True, "False": False}).astype("boolean")
    bad = s.notna() & out.isna()
    if bad.any():
        raise ValueError(f"unexpected onpromotion values: {s[bad].unique()[:10]}")
    return out


# ---------------------------------------------------------------- pass (a)
def pass_a():
    """Months with rows per store (whole window) and training-part sales per store."""
    month_parts, sales_parts = [], []
    for i, ch in enumerate(read_chunks(["date", "store_nbr", "unit_sales"])):
        if ch["date"].min() > WIN_END:                 # file is sorted by date
            break
        ch = ch[(ch["date"] >= WIN_START) & (ch["date"] <= WIN_END)].copy()
        if ch.empty:
            continue
        ch["month"] = ch["date"].dt.to_period("M")
        month_parts.append(ch[["store_nbr", "month"]].drop_duplicates())
        tr = ch[ch["date"] <= TRAIN_END]
        sales_parts.append(tr.groupby("store_nbr")["unit_sales"].sum())
        print(f"  (a) chunk {i:2d}: {ch['date'].min().date()} -> {ch['date'].max().date()}")
    store_months = pd.concat(month_parts).drop_duplicates()
    n_months = store_months.groupby("store_nbr")["month"].nunique()
    store_sales = pd.concat(sales_parts).groupby(level=0).sum()
    assert store_months["month"].nunique() == 24, "window must contain 24 months"
    return n_months, store_sales


def choose_stores(n_months, store_sales):
    """Round-robin over types A-E, biggest training sales first, <= MAX_PER_CITY per city."""
    stores = pd.read_csv(STORES_CSV)
    eligible = stores[stores["store_nbr"].isin(n_months[n_months == 24].index)].copy()
    eligible["train_sales"] = eligible["store_nbr"].map(store_sales)
    eligible = eligible.sort_values("train_sales", ascending=False)

    chosen, city_count = [], {}
    pools = {t: g for t, g in eligible.groupby("type")}
    while len(chosen) < N_STORES:
        added = False
        for t in sorted(pools):
            if len(chosen) == N_STORES:
                break
            for _, row in pools[t].iterrows():
                if row.store_nbr in chosen or city_count.get(row.city, 0) >= MAX_PER_CITY:
                    continue
                chosen.append(int(row.store_nbr))
                city_count[row.city] = city_count.get(row.city, 0) + 1
                added = True
                break
        if not added:
            break

    excluded = n_months[n_months < 24].sort_values()
    print(f"  eligible stores (all 24 months): {len(eligible)} of {len(n_months)}")
    print(f"  excluded (store: months): {excluded.to_dict()}")
    sel = eligible[eligible["store_nbr"].isin(chosen)]
    print(sel[["store_nbr", "city", "state", "type", "cluster", "train_sales"]]
          .to_string(index=False))
    return sorted(chosen)


# ---------------------------------------------------------------- pass (b)
def pass_b(chosen_stores):
    """Per item, on the training part in the chosen stores: total sales and weeks sold."""
    n_weeks = ((TRAIN_END - WIN_START).days + 1) // 7  # 91 full weeks
    week_parts, total_parts = [], []
    for i, ch in enumerate(read_chunks(["date", "store_nbr", "item_nbr", "unit_sales"])):
        if ch["date"].min() > TRAIN_END:               # never look at the test months
            break
        ch = ch[(ch["date"] >= WIN_START) & (ch["date"] <= TRAIN_END)
                & ch["store_nbr"].isin(chosen_stores)].copy()
        if ch.empty:
            continue
        total_parts.append(ch.groupby("item_nbr")["unit_sales"].sum())
        ch["week"] = (ch["date"] - WIN_START).dt.days // 7
        sold = ch[(ch["unit_sales"] > 0) & (ch["week"] < n_weeks)]
        week_parts.append(sold[["item_nbr", "week"]].drop_duplicates())
        print(f"  (b) chunk {i:2d}: {ch['date'].min().date()} -> {ch['date'].max().date()}")

    weeks_sold = (pd.concat(week_parts).drop_duplicates()
                  .groupby("item_nbr")["week"].nunique())
    stats = pd.DataFrame({"total_sales": pd.concat(total_parts).groupby(level=0).sum()})
    stats["weeks_sold"] = weeks_sold.reindex(stats.index).fillna(0).astype(int)
    stats["week_share"] = stats["weeks_sold"] / n_weeks
    items = pd.read_csv(ITEMS_CSV).set_index("item_nbr")
    return stats.join(items[["family", "class", "perishable"]])


def choose_items(stats):
    """Ranked by total sales with constraints, filled in 3 phases (see module docstring)."""
    cands = stats[stats["week_share"] >= MIN_WEEK_SHARE].sort_values(
        "total_sales", ascending=False)
    print(f"  candidates (>= {MIN_WEEK_SHARE:.0%} of weeks): {len(cands)} of {len(stats)} items")

    chosen, fam_count = [], {}

    def ok(item, fam):
        return (item not in chosen and fam_count.get(fam, 0) < MAX_PER_FAMILY
                and len(chosen) < N_ITEMS)

    def add(item, fam):
        chosen.append(item)
        fam_count[fam] = fam_count.get(fam, 0) + 1

    # phase 1: best-selling perishables until MIN_PERISH
    n_perish = 0
    for item, r in cands[cands["perishable"] == 1].iterrows():
        if n_perish >= MIN_PERISH:
            break
        if ok(item, r.family):
            add(item, r.family)
            n_perish += 1

    # phase 2: best item of each missing family until MIN_FAMILIES
    if len(fam_count) < MIN_FAMILIES:
        best_of_fam = (cands[~cands["family"].isin(list(fam_count))]
                       .groupby("family", sort=False).head(1))
        for item, r in best_of_fam.iterrows():
            if len(fam_count) >= MIN_FAMILIES:
                break
            if ok(item, r.family):
                add(item, r.family)

    # phase 3: fill with the best remaining candidates
    for item, r in cands.iterrows():
        if len(chosen) >= N_ITEMS:
            break
        if ok(item, r.family):
            add(item, r.family)

    sel = cands.loc[chosen]
    n_p = int(sel["perishable"].sum())
    checks = {
        f"items == {N_ITEMS}": len(sel) == N_ITEMS,
        f"perishable >= {MIN_PERISH} (got {n_p})": n_p >= MIN_PERISH,
        f"families >= {MIN_FAMILIES} (got {sel['family'].nunique()})":
            sel["family"].nunique() >= MIN_FAMILIES,
        f"max per family <= {MAX_PER_FAMILY} (got {sel['family'].value_counts().max()})":
            sel["family"].value_counts().max() <= MAX_PER_FAMILY,
        f"min week_share >= {MIN_WEEK_SHARE:.2f} (got {sel['week_share'].min():.2f})":
            sel["week_share"].min() >= MIN_WEEK_SHARE,
    }
    for k, v in checks.items():
        print(("  PASS - " if v else "  FAIL - ") + k)
    if not all(checks.values()):
        raise RuntimeError("item selection does not meet the T4 rules")
    print("  items per family:", sel["family"].value_counts().to_dict())
    return sorted(int(x) for x in chosen)


# ---------------------------------------------------------------- pass (c)
def pass_c(chosen_stores, chosen_items):
    """Rows of chosen stores x items over the whole window, item info joined."""
    parts = []
    for i, ch in enumerate(read_chunks(USECOLS)):
        if ch["date"].min() > WIN_END:
            break
        ch = ch[(ch["date"] >= WIN_START) & (ch["date"] <= WIN_END)
                & ch["store_nbr"].isin(chosen_stores)
                & ch["item_nbr"].isin(chosen_items)].copy()
        if ch.empty:
            continue
        ch["onpromotion"] = to_bool_promo(ch["onpromotion"])
        parts.append(ch)
        print(f"  (c) chunk {i:2d}: kept {len(ch):>9,} rows")
    sample = pd.concat(parts, ignore_index=True)

    items = pd.read_csv(ITEMS_CSV)
    sample = sample.merge(items[["item_nbr", "family", "class", "perishable"]],
                          on="item_nbr", how="left", validate="many_to_one")
    assert sample["family"].notna().all(), "some items were not found in items.csv"
    sample["family"] = sample["family"].astype("category")
    sample["class"] = sample["class"].astype("int16")
    sample["perishable"] = sample["perishable"].astype("int8")
    sample = sample.sort_values(["date", "store_nbr", "item_nbr"]).reset_index(drop=True)

    n_dup = sample.duplicated(["date", "store_nbr", "item_nbr"]).sum()
    assert n_dup == 0, f"{n_dup} duplicate (date, store, item) rows"
    return sample


# ---------------------------------------------------------------- summary
def summarize(s, pass_a_time):
    """Markdown table for the PR description."""
    item_tbl = s.drop_duplicates("item_nbr")
    n_items = s["item_nbr"].nunique()
    n_perish = int(item_tbl["perishable"].sum())
    return f"""| Metric | Value |
|---|---|
| Rows | {len(s):,} |
| First date | {s['date'].min().date()} |
| Last date | {s['date'].max().date()} |
| Stores | {s['store_nbr'].nunique()} |
| Items | {n_items} |
| Perishable items | {n_perish} / {n_items} = {n_perish / n_items:.1%} |
| Families | {item_tbl['family'].nunique()} |
| Empty onpromotion | {s['onpromotion'].isna().mean():.2%} of rows |
| Negative unit_sales rows | {int((s['unit_sales'] < 0).sum()):,} |
| First pass (a) time | {pass_a_time:.0f} s |"""


# ---------------------------------------------------------------- main
def main(overwrite=False):
    if not os.path.exists(TRAIN_CSV):
        raise FileNotFoundError(f"{TRAIN_CSV} not found. Run the extraction cell first "
                                "(a session reset wipes /content).")
    if os.path.exists(SALES_SAMPLE) and not overwrite:
        raise FileExistsError(f"{SALES_SAMPLE} already exists. v1 is not overwritten "
                              "silently: delete it on purpose or use --overwrite.")
    t_all = time.time()

    print("PASS (a): stores")
    t0 = time.time()
    n_months, store_sales = pass_a()
    pass_a_time = time.time() - t0
    print(f"  pass (a) time: {pass_a_time:.0f} s")
    chosen_stores = choose_stores(n_months, store_sales)
    print(f"  CHOSEN_STORES = {chosen_stores}")

    print("PASS (b): items")
    t0 = time.time()
    stats = pass_b(chosen_stores)
    print(f"  pass (b) time: {time.time() - t0:.0f} s")
    chosen_items = choose_items(stats)

    print("PASS (c): sample")
    t0 = time.time()
    sample = pass_c(chosen_stores, chosen_items)
    print(f"  pass (c) time: {time.time() - t0:.0f} s")

    os.makedirs(os.path.dirname(SALES_SAMPLE), exist_ok=True)
    sample.to_parquet(SALES_SAMPLE, index=False)
    print(f"saved: {SALES_SAMPLE} ({os.path.getsize(SALES_SAMPLE) / 1e6:.1f} MB)")

    print("\nSUMMARY (paste in the PR)")
    print(summarize(pd.read_parquet(SALES_SAMPLE), pass_a_time))
    print(f"\ntotal time: {time.time() - t_all:.0f} s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T4: build sales_sample_v1.parquet")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace an existing sales_sample_v1.parquet")
    main(overwrite=parser.parse_args().overwrite)
