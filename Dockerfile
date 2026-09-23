# Dockerfile
# Containerizes the pipeline so it runs identically on any machine -
# no "works on my laptop" dependency on a local Python version or
# whatever dbt happens to be installed globally.

FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal on purpose - this pipeline has no compiled
# dependencies beyond what pandas/duckdb ship as wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# raw/, data/, and warehouse.duckdb are all meant to be mounted as
# volumes (see docker-compose.yml) so pipeline output survives
# container restarts instead of living only inside the image layer.
VOLUME ["/app/raw", "/app/data"]

ENTRYPOINT ["python", "orchestration/run_daily.py"]