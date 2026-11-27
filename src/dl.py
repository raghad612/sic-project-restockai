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
