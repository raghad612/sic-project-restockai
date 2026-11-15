# Saves the three small Favorita tables (stores, items, holidays_events) as parquet in Drive.
# Run in Colab after the CSVs are extracted to LOCAL (see Issue #17, step 1).
import os

import pandas as pd

from src.config import LOCAL, STORES_OUT, ITEMS_OUT, HOLIDAYS_OUT


def main():
    # Read everything as it is; these tables are tiny, so no chunking is needed.
    stores = pd.read_csv(f"{LOCAL}/stores.csv")
    items = pd.read_csv(f"{LOCAL}/items.csv")
    holidays = pd.read_csv(f"{LOCAL}/holidays_events.csv")

    # Real dates, so later tasks can filter and merge by date without converting again.
    holidays["date"] = pd.to_datetime(holidays["date"])

    # Small integer types keep the files light; the ID columns are the join keys.
    stores = stores.astype({"store_nbr": "int32", "cluster": "int16"})
    items = items.astype({"item_nbr": "int32", "class": "int16", "perishable": "int8"})

    # Stop if the shared Drive folder isn't visible (e.g. Drive not mounted), instead of silently writing to Colab's disk.
    if not os.path.isdir(os.path.dirname(STORES_OUT)):
        raise FileNotFoundError("restockai-work/interim not found. Is Drive mounted?")

    # Full tables, no rows dropped: cleaning decisions belong to later tasks.
    stores.to_parquet(STORES_OUT, index=False)
    items.to_parquet(ITEMS_OUT, index=False)
    holidays.to_parquet(HOLIDAYS_OUT, index=False)

    print(f"stores:   {len(stores):,} rows -> {STORES_OUT}")
    print(f"items:    {len(items):,} rows -> {ITEMS_OUT}")
    print(f"holidays: {len(holidays):,} rows -> {HOLIDAYS_OUT}")
    print(f"unique families in items: {items['family'].nunique()}")
    print(f"holidays date dtype: {holidays['date'].dtype}")


if __name__ == "__main__":
    main()