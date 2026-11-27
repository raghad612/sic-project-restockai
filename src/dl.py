import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

# Model contract (from Raghad):
# inputs: dict with int32 arrays of shape (n, 1) for each key in cardinalities
#         (family, class, store; dow and month only if kept) + "numeric" float32 (n, n_numeric)
# cardinalities[key] = number of categories + 1 (index 0 = unknown)
# target: log1p(sales), loss = L1 (mae), output is linear; predict with expm1 and clip at 0

CONFIG_A = {"hidden_units": [128, 64], "dropout": 0.2, "learning_rate": 0.001,
            "embed_dim": 4, "calendar_embed_dim": 3}
CONFIG_B = {"hidden_units": [256, 128, 64], "dropout": 0.3, "learning_rate": 0.001,
            "embed_dim": 4, "calendar_embed_dim": 3}
CONFIG_C = {"hidden_units": [128, 64], "dropout": 0.2, "learning_rate": 0.0005,
            "embed_dim": 4, "calendar_embed_dim": 3}


def build_model(config, cardinalities, n_numeric):
    inputs, parts = {}, []

    # One embedding per category key present in cardinalities
    for name, n_cat in cardinalities.items():
        inp = keras.Input(shape=(1,), dtype="int32", name=name)
        dim = config["calendar_embed_dim"] if name in ("dow", "month") else config["embed_dim"]
        # input_dim = n_cat already includes the +1 "unknown" slot (index 0)
        emb = layers.Embedding(input_dim=n_cat, output_dim=dim, name=f"emb_{name}")(inp)
        parts.append(layers.Flatten(name=f"flat_{name}")(emb))
        inputs[name] = inp

    # Numeric block: scaled lags, rolling means, missing flags, 0/1 flags
    num = keras.Input(shape=(n_numeric,), dtype="float32", name="numeric")
    inputs["numeric"] = num
    parts.append(num)

    x = layers.Concatenate(name="concat")(parts)

    # Dropout after every hidden layer except the last
    units_list = config["hidden_units"]
    for i, units in enumerate(units_list):
        x = layers.Dense(units, activation="relu", name=f"dense_{i}")(x)
        if i < len(units_list) - 1:
            x = layers.Dropout(config["dropout"], name=f"drop_{i}")(x)

    out = layers.Dense(1, name="output")(x)

    model = keras.Model(inputs=inputs, outputs=out, name="mlp")
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=config["learning_rate"]),
                  loss="mae")
    return model


# ---- T13 feature preparation (Ali). Settings: each team decision is one line here.
CATEGORY_KEYS = {"family": "family", "class": "class", "store_nbr": "store_nbr",
                 "dow": "weekday", "month": "month"}          # input key -> column
HISTORY_COLS = ["lag_1", "lag_7", "lag_14", "roll_mean_7", "roll_mean_28"]
FLAG_COLS = ["onpromotion", "perishable", "quake_period",
             "hol_national_dayoff", "hol_national_shopping", "hol_local"]
MISSING_FLAG_COLS = ["lag_1", "lag_14"]
EXTRA_NUMERIC = []   # e.g. ["day_of_month", "week_of_year"] if the team wants them
# Not inputs (leakage or not allowed): is_filled, is_return, unit_sales, item_nbr,
# date, fill_after_last_train.


def fit_prep(fit_df):
    """Learn the preparation statistics from training rows only."""
    stats = {"median": {}, "mean": {}, "std": {}, "vocab": {}}
    for c in MISSING_FLAG_COLS:
        stats["median"][c] = float(fit_df[c].median())
    for c in HISTORY_COLS:
        x = fit_df[c].fillna(stats["median"].get(c, 0.0))
        x = np.log1p(x.astype("float64"))
        stats["mean"][c] = float(x.mean())
        stats["std"][c] = float(x.std())
    for c in EXTRA_NUMERIC:
        stats["mean"][c] = float(fit_df[c].mean())
        stats["std"][c] = float(fit_df[c].std())
    for key, col in CATEGORY_KEYS.items():
        cats = sorted(fit_df[col].dropna().unique().tolist())
        stats["vocab"][key] = {v: i + 1 for i, v in enumerate(cats)}   # 0 = unknown
    return stats


def apply_prep(df, stats):
    """Turn rows into model inputs with the frozen statistics. Returns (inputs, y)."""
    numeric = []
    for c in HISTORY_COLS:
        x = df[c].fillna(stats["median"].get(c, 0.0)).astype("float64")
        x = (np.log1p(x) - stats["mean"][c]) / stats["std"][c]
        numeric.append(x.to_numpy())
    for c in FLAG_COLS:
        numeric.append(df[c].fillna(0).astype("float64").to_numpy())
    for c in MISSING_FLAG_COLS:
        numeric.append(df[c].isna().astype("float64").to_numpy())
    for c in EXTRA_NUMERIC:
        numeric.append(((df[c] - stats["mean"][c]) / stats["std"][c]).to_numpy())
    inputs = {"numeric": np.column_stack(numeric).astype("float32")}
    for key, col in CATEGORY_KEYS.items():
        idx = df[col].astype("object").map(stats["vocab"][key]).fillna(0).astype("int32")
        inputs[key] = idx.to_numpy().reshape(-1, 1)
    y = np.log1p(df["target"].astype("float64")).to_numpy().astype("float32")
    return inputs, y


def cardinalities(stats):
    """Vocabulary size + 1 (index 0 = unknown) for each category key."""
    return {key: len(v) + 1 for key, v in stats["vocab"].items()}
