
"""T9: Seven-day naive baseline and evaluation."""

import argparse
import os

import pandas as pd

from src.config import FEATURES, BASELINE_PREDICTIONS, BASELINE_METRICS
from src.metrics import mae, wape
from src.split import split_by_date


KG_FAMILIES = {"POULTRY", "MEATS", "PRODUCE"}
MIXED_FAMILIES = {"PREPARED FOODS", "FROZEN FOODS"}


def evaluate_period(data, name):
    """Score eligible rows using the existing lag_7 feature."""
    missing_lag = data["lag_7"].isna()
    flagged = data["fill_after_last_train"]

    eligible = data.loc[~missing_lag & ~flagged].copy()

    if eligible.empty:
        raise ValueError(f"No eligible rows in {name}")

    if eligible["target"].isna().any():
        raise ValueError(f"Missing target values in {name}")

    eligible["prediction"] = eligible["lag_7"]

    print(f"\n{name}")
    print(f"Total rows: {len(data):,}")
    print(f"Missing lag_7: {missing_lag.sum():,}")
    print(f"Flagged rows: {flagged.sum():,}")
    print(f"Excluded (unique rows): {len(data) - len(eligible):,}")
    print(f"Scored rows: {len(eligible):,}")

    results = []

    for family, group in eligible.groupby("family", observed=True):
        family = str(family).strip().upper()

        if family in KG_FAMILIES:
            unit_type = "kg"
        elif family in MIXED_FAMILIES:
            unit_type = "mixed"
        else:
            unit_type = "count"

        results.append({
            "period": name,
            "family": family,
            "unit_type": unit_type,
            "rows": len(group),
            "MAE": mae(group["target"], group["prediction"]),
            "WAPE_percent": wape(group["target"], group["prediction"]),
        })

    count_rows = eligible.loc[
        ~eligible["family"].astype(str).str.strip().str.upper().isin(
            KG_FAMILIES | MIXED_FAMILIES
        )
    ]

    if count_rows.empty:
        raise ValueError(f"No count-family rows in {name}")

    results.append({
        "period": name,
        "family": "COUNT_OVERALL",
        "unit_type": "count",
        "rows": len(count_rows),
        "MAE": mae(count_rows["target"], count_rows["prediction"]),
        "WAPE_percent": wape(count_rows["target"], count_rows["prediction"]),
    })

    results_df = pd.DataFrame(results)

    overall = results_df.loc[
        results_df["family"] == "COUNT_OVERALL"
    ].iloc[0]

    print("Count-family overall MAE:", overall["MAE"])
    print("Count-family overall WAPE (%):", overall["WAPE_percent"])

    print("\nPer-family results:")
    print(
        results_df.loc[
            results_df["family"] != "COUNT_OVERALL"
        ].to_string(index=False)
    )

    predictions = eligible[
        ["date", "store_nbr", "item_nbr", "prediction", "target"]
    ].copy()

    return predictions, results_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing output files",
    )
    args = parser.parse_args()

    if not os.path.isfile(FEATURES):
        raise FileNotFoundError(FEATURES)

    if os.path.exists(BASELINE_METRICS) and not args.overwrite:
        raise FileExistsError(
            f"{BASELINE_METRICS} already exists. "
            "Use --overwrite to replace it."
        )

    df = pd.read_parquet(FEATURES)
    fit, validation, test = split_by_date(df)

    print(f"\nFit rows (flagged excluded): {len(fit):,}")

    val_predictions, val_results = evaluate_period(
        validation, "validation"
    )
    test_predictions, test_results = evaluate_period(
        test, "test"
    )

    predictions = pd.concat(
        [val_predictions, test_predictions],
        ignore_index=True,
    )

    results = pd.concat(
        [val_results, test_results],
        ignore_index=True,
    )

    os.makedirs(os.path.dirname(BASELINE_METRICS), exist_ok=True)

    if os.path.exists(BASELINE_PREDICTIONS):
        if args.overwrite:
            predictions.to_parquet(BASELINE_PREDICTIONS, index=False)
            print(f"\nPredictions overwritten: {BASELINE_PREDICTIONS}")
        else:
            existing = pd.read_parquet(BASELINE_PREDICTIONS)
            if not existing.equals(predictions):
                raise ValueError(
                    "Existing predictions differ from the current run. "
                    "Metrics were not saved."
                )
            print("\nExisting predictions verified; not overwritten.")
    else:
        predictions.to_parquet(BASELINE_PREDICTIONS, index=False)
        print(f"\nPredictions saved to: {BASELINE_PREDICTIONS}")

    results.to_csv(BASELINE_METRICS, index=False)

    print(f"Metrics saved to: {BASELINE_METRICS}")
    print(f"Total prediction rows: {len(predictions):,}")
    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()
