
"""T9: Fixed chronological fit, validation, and test split."""

import pandas as pd

from src.config import (
    FIT_END,
    VAL_START,
    VAL_END,
    TEST_START,
    TEST_END,
)


def split_by_date(df):
    """Split by calendar date; exclude future-dependent rows from fitting."""
    dates = pd.to_datetime(df["date"])

    fit = df.loc[
        (dates <= FIT_END) & (~df["fill_after_last_train"])
    ].copy()

    validation = df.loc[
        dates.between(VAL_START, VAL_END)
    ].copy()

    test = df.loc[
        dates.between(TEST_START, TEST_END)
    ].copy()

    for name, part in [
        ("Fit", fit),
        ("Validation", validation),
        ("Test", test),
    ]:
        print(
            f"{name}: {len(part):,} rows, "
            f"{part['date'].min()} to {part['date'].max()}"
        )

    return fit, validation, test
