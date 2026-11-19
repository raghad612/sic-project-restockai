"""T7 cleaning: sales_sample_v1 -> sales_clean_v1 + quarantine. (Issue #23)"""
import pandas as pd
from config import SALES_SAMPLE, SALES_CLEAN, SALES_QUARANTINE


def find_bad_rows(df):
    """Leen: duplicate, null and type checks.
    Returns (bad_rows with 'reason' column, good_df)."""
    raise NotImplementedError  # Leen fills this in


def main():
    pass  # Ali: load, date/window checks, quarantine, summary


if __name__ == "__main__":
    main()
