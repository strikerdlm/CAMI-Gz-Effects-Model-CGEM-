# cgem-ext API image — Phase 5
#
# Single-stage build. The compiled FAA Fortran binary (`cgem`) and the
# canonical paper-1 dataset + sensitivity CSVs ship inside the image so
# `/run-cgem` and `/sensitivity/{target}` work out of the box.
#
# Build:
#   docker build -f cgem_ext/api/Dockerfile -t cgem-ext-api:0.1.0 .
#
# Run:
#   docker run --rm -p 8000:8000 cgem-ext-api:0.1.0
#
# Push to GHCR (paper-1 reproducibility):
#   docker tag cgem-ext-api:0.1.0 ghcr.io/strikerdlm/cgem-ext-api:0.1.0
#   docker push ghcr.io/strikerdlm/cgem-ext-api:0.1.0

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Fortran runtime needed by the compiled cgem binary (libgfortran5.so).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the Python package + ML + API extras.
COPY pyproject.toml requirements.txt /app/
RUN pip install -e .[ml,api]

# Copy the rest of the repo. Order matters for layer caching: code that
# changes most often (cgem_ext/) is copied last so dependency layers
# stay cached across iterations.
COPY src /app/src
COPY cgem cgem.exe gloc_inp.dat /app/
COPY *.py /app/
COPY Aerobatics_sample_inputs /app/Aerobatics_sample_inputs
COPY data/datasets/cgem_synthetic_v1.parquet /app/data/datasets/
COPY data/datasets/cgem_synthetic_v1.meta.json /app/data/datasets/
COPY data/results /app/data/results
COPY tools /app/tools
COPY cgem_ext /app/cgem_ext

EXPOSE 8000

# Healthcheck hits /healthz; the lifespan startup is ~30 s so we give it
# 90 s before the first probe.
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD python -c "import urllib.request, sys; r = urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3); sys.exit(0 if r.status == 200 else 1)"

CMD ["uvicorn", "cgem_ext.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
