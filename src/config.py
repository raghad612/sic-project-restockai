# One place for shared paths, so nobody hardcodes them in notebooks.
# Everyone must have the shared folders as shortcuts in My Drive with these exact names.
RAW = "/content/drive/MyDrive/restockai-raw"        # original data, read-only
WORK = "/content/drive/MyDrive/restockai-work"      # everything we generate
INTERIM = f"{WORK}/interim"                         # cleaned data
PROCESSED = f"{WORK}/processed"                     # features and splits
OUTPUTS = f"{WORK}/outputs"                         # predictions and metrics

SEED = 42  # fixed random seed so results can be repeated

# T4 additions
ZIP_PATH = f"{RAW}/favorita-grocery-sales-forecasting.zip"  # raw zip in Drive
LOCAL = "/content/favorita"  # Colab local disk only: wiped on reset, never Drive or GitHub

# versioned output names (one writer per file, see DATA.md)
SALES_SAMPLE = f"{INTERIM}/sales_sample_v1.parquet"
STORES_OUT = f"{INTERIM}/stores_v1.parquet"
ITEMS_OUT = f"{INTERIM}/items_v1.parquet"
HOLIDAYS_OUT = f"{INTERIM}/holidays_events_v1.parquet"
