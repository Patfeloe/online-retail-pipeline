"""
run_daily.py

Plain-Python orchestrator: extract -> load -> dbt run -> dbt test,
for a single date. Wire this into cron for a scheduled version:

    0 6 * * * cd /path/to/retail-pipeline && python orchestration/run_daily.py --date $(date -d yesterday +\\%F)

Or convert into an Airflow DAG later by turning each subprocess call
into its own PythonOperator/BashOperator task with the same
dependency chain (extract >> load >> dbt_run >> dbt_test).
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_step(description: str, cmd: list[str], cwd: Path = ROOT) -> None:
    print(f"\n=== {description} ===")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(f"Step failed: {description} (exit code {result.returncode})")


def run_daily(target_date: str, source: str) -> None:
    run_step(
        "Extract",
        [sys.executable, "extract/extract_daily.py", "--date", target_date, "--source", source],
    )
    run_step(
        "Load",
        [sys.executable, "load/load_to_staging.py", "--date", target_date],
    )
    run_step(
        "Transform (dbt run)",
        ["dbt", "run", "--profiles-dir", "transform", "--project-dir", "transform"],
    )
    run_step(
        "Data quality (dbt test)",
        ["dbt", "test", "--profiles-dir", "transform", "--project-dir", "transform"],
    )
    print(f"\nPipeline completed successfully for {target_date}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full daily pipeline for one date")
    parser.add_argument("--date", required=True, help="Date to process, YYYY-MM-DD")
    parser.add_argument("--source", default="data/online_retail.csv",
                         help="Path to the full source CSV")
    args = parser.parse_args()
    run_daily(args.date, args.source)