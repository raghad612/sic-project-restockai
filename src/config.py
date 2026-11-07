# One place for shared paths, so nobody hardcodes them in notebooks.
# Everyone must have the shared folders as shortcuts in My Drive with these exact names.
RAW = "/content/drive/MyDrive/restockai-raw"        # original data, read-only
WORK = "/content/drive/MyDrive/restockai-work"      # everything we generate
INTERIM = f"{WORK}/interim"                         # cleaned data
PROCESSED = f"{WORK}/processed"                     # features and splits
OUTPUTS = f"{WORK}/outputs"                         # predictions and metrics

SEED = 42  # fixed random seed so results can be repeated
