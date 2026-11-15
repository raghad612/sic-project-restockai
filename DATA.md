# Shared data log

Data lives in Google Drive, not in this repo.
- restockai-raw: original files (read-only for the team)
- restockai-work: generated files (interim, processed, outputs)

Do not paste Drive links here, because this repo is public. The leader shares the folder directly.

| File | Folder | Made by | Script | Date |
|------|--------|---------|--------|------|
| favorita-grocery-sales-forecasting.zip (458 MiB, contains 8 .7z files) | restockai-raw | Raghad | Manual Colab cell using the Kaggle API (token in Colab Secrets, not in repo) | 2026-11-12 |
| sales_sample_v1.parquet (5.6 MB, 1,741,225 rows: 12 stores x 250 items, 2015-08-01 to 2017-07-31) | restockai-work/interim | Ali | src/subsample.py | 2026-11-15 |
| stores_v1.parquet (<0.01 MB, 54 rows, full stores.csv) | restockai-work/interim | Leen | src/small_tables.py | 2026-11-14 |
| items_v1.parquet (0.03 MB, 4,100 rows, full items.csv) | restockai-work/interim | Leen | src/small_tables.py | 2026-11-14 |
| holidays_events_v1.parquet (0.01 MB, 350 rows, full holidays_events.csv) | restockai-work/interim | Leen | src/small_tables.py | 2026-11-14 |
