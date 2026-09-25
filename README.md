WTC-MEK2QF5V

# online-retail-pipeline

A small end-to-end data pipeline: extract daily sales data, load it into a database, transform it into clean tables, and test the results — all automated.

Built using the UCI Online Retail dataset as a stand-in for a store's daily point-of-sale export.

## How it works

```
raw CSV (daily)  →  DuckDB staging table  →  dbt models  →  marts
   extract              load                  transform
```

1. **Extract** — pulls one day's orders and saves them as a raw file
2. **Load** — inserts that day's data into a database table (safe to re-run without duplicating data)
3. **Transform** — dbt builds clean fact/dimension tables and a few summary reports (daily revenue, top products, repeat customers)
4. **Test** — dbt checks the data for missing values, duplicates, and bad records
5. **Orchestrate** — one script runs all of the above in order

## Setup

```
pip install -r requirements.txt
```

Download the dataset from [UCI's Online Retail page](https://archive.ics.uci.edu/dataset/352/online+retail) and save it as `data/online_retail.csv`.

## Run it

```
python orchestration/run_daily.py --date 2011-01-05
```

(Pick any date between 2010-12-01 and 2011-12-09 — that's the range the dataset covers.)

## Run it with Docker

```
docker compose build
docker compose run --rm pipeline --date 2011-01-05
```

## Check the results

```
duckdb warehouse.duckdb
select * from daily_revenue order by date_day desc limit 10;
select * from top_products order by total_revenue desc limit 10;
```

## What's automated

- **CI**: every push runs the pipeline against a small sample dataset and checks that all data quality tests still pass (see `.github/workflows/dbt-tests.yml`)
- **Docker**: the whole pipeline runs in a container, so it works the same way on any machine.

## What this doesn't cover

This is a portfolio-scale project, not a production system — it runs on a laptop, uses a single static data source, and has no live scheduling or cloud deployment. Those would be the next things to add.
