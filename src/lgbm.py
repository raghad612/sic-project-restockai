"""T10: LightGBM point forecast."""

import lightgbm as lgb

from src.config import SEED
from src.evaluate import eligible_rows

SET_A = [
    "lag_1", "lag_7", "lag_14", "roll_mean_7", "roll_mean_28",
    "weekday", "day_of_month", "month", "week_of_year",
    "hol_national_dayoff", "hol_national_shopping", "hol_local",
    "quake_period", "onpromotion", "family", "class", "perishable",
]
SET_B = SET_A + ["store_nbr"]

START_PARAMS = {
    "objective": "regression_l1",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 100,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "n_estimators": 2000,
    "seed": SEED,
}


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


def train(fit, validation, features, params):
    """Step 3: fit on fit rows, early stopping on scored validation rows."""
    assert not fit["fill_after_last_train"].any(), "flagged rows in fit"
    fit = prepare(fit)
    validation = eligible_rows(prepare(validation))
    model = lgb.LGBMRegressor(**params)
    model.fit(
        fit[features], fit["target"],
        eval_set=[(validation[features], validation["target"])],
        callbacks=[lgb.early_stopping(50)],
    )
    return model


def predict(model, data, features):
    """Predict the scored rows, clipped at 0 because demand is never negative."""
    data = eligible_rows(prepare(data))
    data["prediction"] = model.predict(data[features]).clip(0, None)
    return data
