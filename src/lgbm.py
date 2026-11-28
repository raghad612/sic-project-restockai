"""T10: LightGBM point forecast."""


SET_A = [
    "lag_1", "lag_7", "lag_14", "roll_mean_7", "roll_mean_28",
    "weekday", "day_of_month", "month", "week_of_year",
    "hol_national_dayoff", "hol_national_shopping", "hol_local",
    "quake_period", "onpromotion", "family", "class", "perishable",
]
SET_B = SET_A + ["store_nbr"]


def prepare(data, fill_promo=True):
    """Step 2 NaN rule. onpromotion is NaN only on zero-filled rows (target 0),
    so NaN would leak the answer: it becomes 0 (no promotion)."""
    data = data.copy()
    nan_promo = data["onpromotion"].isna()
    print(f"NaN onpromotion rows: {nan_promo.sum():,} "
          f"(target 0: {(data.loc[nan_promo, 'target'] == 0).sum():,})")
    if fill_promo:
        data["onpromotion"] = data["onpromotion"].fillna(0)
    data["store_nbr"] = data["store_nbr"].astype("category")
    return data
