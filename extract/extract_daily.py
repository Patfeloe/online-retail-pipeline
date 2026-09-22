"""
extract_daily.py

Simulates a daily POS export by slicing a full historical dataset down to
one day's worth of invoices and landing it, untouched, in the raw zone.

This stands in for "pull yesterday's export from the store's POS system" -
in a real pipeline this function body would call an API or read from a
drop folder instead of slicing a static file.

Usage:
    python extract_daily.py --date 2011-01-05 --source data/online_retail.csv

Source dataset: UCI "Online Retail" dataset
https://archive.ics.uci.edu/dataset/352/online+retail
Expected columns: InvoiceNo, StockCode, Description, Quantity,
                   InvoiceDate, UnitPrice, CustomerID, Country
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "raw"


def extract_day(source_path: Path, target_date: str) -> Path:
    """Filter the source dataset to a single calendar date and write it
    to raw/date=<target_date>/orders.csv. Never overwrites a prior day;
    re-running the same date overwrites only that date's own partition,
    which keeps this step idempotent."""

    if not source_path.exists():
        sys.exit(f"Source file not found: {source_path}")

    df = pd.read_csv(source_path, encoding="ISO-8859-1")

    # Normalize column names in case the source uses different casing
    df.columns = [c.strip() for c in df.columns]

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    day_start = pd.to_datetime(target_date)
    day_end = day_start + pd.Timedelta(days=1)

    day_df = df[(df["InvoiceDate"] >= day_start) & (df["InvoiceDate"] < day_end)]

    if day_df.empty:
        print(f"WARNING: no rows found for {target_date}. "
              f"Dataset covers {df['InvoiceDate'].min().date()} "
              f"to {df['InvoiceDate'].max().date()}.")

    partition_dir = RAW_DIR / f"date={target_date}"
    partition_dir.mkdir(parents=True, exist_ok=True)
    out_path = partition_dir / "orders.csv"

    day_df.to_csv(out_path, index=False)
    print(f"Wrote {len(day_df)} rows to {out_path}")
    return out_path


def backfill(source_path: Path, start_date: str, end_date: str) -> None:
    """Loop extract_day across a date range - used to populate history
    in one go rather than day by day."""
    for d in pd.date_range(start_date, end_date, freq="D"):
        extract_day(source_path, d.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract one day's orders into the raw zone")
    parser.add_argument("--date", help="Single date to extract, YYYY-MM-DD")
    parser.add_argument("--start", help="Backfill start date, YYYY-MM-DD")
    parser.add_argument("--end", help="Backfill end date, YYYY-MM-DD")
    parser.add_argument("--source", default="data/online_retail.csv",
                         help="Path to the full source CSV")
    args = parser.parse_args()

    source_path = Path(args.source)

    if args.date:
        extract_day(source_path, args.date)
    elif args.start and args.end:
        backfill(source_path, args.start, args.end)
    else:
        parser.error("Provide either --date, or both --start and --end for a backfill")