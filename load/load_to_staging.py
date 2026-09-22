"""
load_to_staging.py

Reads one day's raw CSV partition and loads it into a staging table.

Uses DuckDB by default (zero setup, single file, good for a portfolio
project). Swap the connection lines for psycopg2/SQLAlchemy if you'd
rather run this against Postgres - the SQL is standard enough to port
directly.

The load is an UPSERT keyed on (invoice_no, stock_code, invoice_date):
re-running the same date replaces that date's rows rather than
duplicating them. That idempotency is the main thing worth being
deliberate about in this whole pipeline.

Usage:
    python load_to_staging.py --date 2011-01-05
"""

import argparse
from pathlib import Path

import duckdb
import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "raw"
DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.duckdb"

STAGING_TABLE = "stg_orders"

CREATE_STAGING_SQL = f"""
CREATE TABLE IF NOT EXISTS {STAGING_TABLE} (
    invoice_no   VARCHAR,
    stock_code   VARCHAR,
    description  VARCHAR,
    quantity     INTEGER,
    invoice_date TIMESTAMP,
    unit_price   DOUBLE,
    customer_id  VARCHAR,
    country      VARCHAR,
    load_date    DATE
);
"""


def load_day(target_date: str) -> None:
    partition_path = RAW_DIR / f"date={target_date}" / "orders.csv"
    if not partition_path.exists():
        raise FileNotFoundError(
            f"No raw partition for {target_date}. Run extract_daily.py first."
        )

    df = pd.read_csv(partition_path, encoding="ISO-8859-1")
    df = df.rename(columns={
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
    })
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["load_date"] = target_date
    df["customer_id"] = df["customer_id"].astype(str)

    con = duckdb.connect(str(DB_PATH))
    con.execute(CREATE_STAGING_SQL)

    # Idempotent load: clear this date's rows, then insert fresh.
    # Safe to re-run for the same date without creating duplicates.
    con.execute(f"DELETE FROM {STAGING_TABLE} WHERE load_date = ?", [target_date])
    con.register("day_df", df)
    con.execute(f"""
        INSERT INTO {STAGING_TABLE}
        SELECT invoice_no, stock_code, description, quantity,
               invoice_date, unit_price, customer_id, country, load_date
        FROM day_df
    """)

    row_count = con.execute(
        f"SELECT COUNT(*) FROM {STAGING_TABLE} WHERE load_date = ?", [target_date]
    ).fetchone()[0]
    print(f"Loaded {row_count} rows for {target_date} into {STAGING_TABLE}")
    con.close()


def backfill(start_date: str, end_date: str) -> None:
    for d in pd.date_range(start_date, end_date, freq="D"):
        date_str = d.strftime("%Y-%m-%d")
        partition_path = RAW_DIR / f"date={date_str}" / "orders.csv"
        if partition_path.exists():
            load_day(date_str)
        else:
            print(f"Skipping {date_str} - no raw partition found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load one day's raw partition into staging")
    parser.add_argument("--date", help="Single date to load, YYYY-MM-DD")
    parser.add_argument("--start", help="Backfill start date, YYYY-MM-DD")
    parser.add_argument("--end", help="Backfill end date, YYYY-MM-DD")
    args = parser.parse_args()

    if args.date:
        load_day(args.date)
    elif args.start and args.end:
        backfill(args.start, args.end)
    else:
        parser.error("Provide either --date, or both --start and --end for a backfill")