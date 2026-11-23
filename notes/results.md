
# ReStock AI — Baseline Results (T9)

## Method

The T9 baseline predicts daily sales using the existing
`lag_7` feature from `features_v1.parquet`.

Prediction = sales of the same store and item 7 days earlier.

The baseline does not train a model or recompute `lag_7`.

## Chronological Split

| Period | Dates | Rows |
|---|---|---:|
| Fit | 2015-08-01 to 2017-03-05 | 1,521,769 |
| Validation | 2017-03-06 to 2017-04-30 | 145,005 |
| Test | 2017-05-01 to 2017-07-31 | 232,489 |

The fit count excludes 1,269 rows flagged
`fill_after_last_train`.

The existing `TRAIN_END` remains 2017-04-30.
No random splitting is used.

## Scoring Rules

- Missing `lag_7` rows are excluded from scoring.
- Rows flagged `fill_after_last_train` are excluded from
  fitting and validation scoring.
- Validation and test are evaluated separately.
- MAE = mean(abs(target - prediction)).
- WAPE (%) = 100 * sum(abs(target - prediction)) / sum(target).
- WAPE is undefined when the sum of targets is zero.
- Metrics are calculated on eligible rows only.

## Excluded Rows

| Check | Validation | Test |
|---|---:|---:|
| Total rows | 145,005 | 232,489 |
| Missing lag_7 | 47 | 162 |
| Flagged rows | 2,559 | 0 |
| Unique excluded rows | 2,594 | 162 |
| Scored rows | 142,411 | 232,327 |

In validation, 12 rows satisfy both exclusion conditions
and are counted only once.

## Family Unit Handling

The following families are classified as kg:
- POULTRY
- MEATS
- PRODUCE

The following families are classified as mixed:
- PREPARED FOODS
- FROZEN FOODS

All other included families are classified as count.

Overall MAE and WAPE are calculated only on count-family
rows to avoid combining incompatible sales units.

Per-family MAE and WAPE are reported separately for all
eligible families.

## Official Stage B Baseline Results

| Metric | Validation | Test |
|---|---:|---:|
| All eligible rows | 142,411 | 232,327 |
| Count-family rows | 101,562 | 165,512 |
| Kg/mixed rows excluded from overall | 40,849 | 66,815 |
| Count-family MAE | 14.512524 | 14.452076 |
| Count-family WAPE (%) | 59.237007 | 59.087923 |

These are the official Stage B results on the current
`features_v1.parquet`, replacing provisional Stage A numbers.

Full per-family metrics are stored in
`baseline_metrics_v1.csv` in the shared outputs folder.

## Outputs

The following files are generated in the shared Drive
outputs directory configured in `src/config.py`:

- `baseline_predictions_v1.parquet`
  - 374,738 rows
  - Columns: date, store_nbr, item_nbr, prediction, target
  - No missing values in these columns

- `baseline_metrics_v1.csv`
  - 31 rows
  - Columns: period, family, unit_type, rows, MAE,
    WAPE_percent
  - Includes COUNT_OVERALL for validation and test
  - No missing values

Output files are not committed to GitHub.

The baseline refuses to overwrite existing metrics without
`--overwrite`. Existing predictions are verified against
the current calculation before metrics are saved.

## Limitations

The existing T8 feature-generation process may allow
some flagged, future-dependent filled rows to influence
later lag features. T9 excludes flagged rows from fitting
and validation scoring but does not rebuild T8 features.

The existing upstream item-selection process also uses
data through 2017-04-30, beyond the updated fit cutoff.
This potential selection bias is not corrected by T9.

These limitations should be considered when interpreting
the baseline and comparing later models.
