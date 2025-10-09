# Quorum Legislative Data

Django app that loads legislative data from CSVs into SQLite and exposes it via REST APIs and a simple web UI.

## Run

- Requirements: Python 3.10+, pip
- Optional: Makefile shortcuts

Using Makefile (recommended):
- `make setup` (create venv, install deps, migrate, load CSVs)
- `make server` (start at http://localhost:8000)

Manual:
- `python3 -m venv .venv && source .venv/bin/activate`
- `pip install --upgrade pip && pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py load_data`  # imports CSVs from `csv_data/` by default
- `python manage.py runserver`

## CSV Loading

- Default directory: `csv_data/` (override with `--csv-dir`)
- Files required: `legislators.csv`, `bills.csv`, `votes.csv`, `vote_results.csv`
- Validation: the loader raises clear errors if references are missing or columns are invalid, e.g.:
  - "Primary sponsor with id=XXX not found (from bills.csv)."
  - "Bill with id=YYY not found (from votes.csv)."
  - "Invalid vote_type 'Z' for vote_result id=ID (expected 1 or 2)."

## API

- Root: `GET /api/`
- Stats: `GET /api/stats/`
- Legislators: `GET /api/legislators/`, `GET /api/legislators/{id}/`
- Bills: `GET /api/bills/`, `GET /api/bills/{id}/`

Pagination: disabled (all results returned).

## Web UI

- Home: `/` (overview stats)
- Legislators: `/legislators/` (counts per legislator)
- Bills: `/bills/` (counts and primary sponsor per bill)
- Detail pages for each legislator and bill

## Tests & Lint

- `make test` or `pytest -q`
- Coverage: `make test-coverage`
- Lint/format: `make lint` or `make fix`

## Project Layout

- `core/` Django settings
- `legislative/` app (models, serializers, views, urls, templates, commands)
- `csv_data/` input CSVs
- `tests/` pytest suite
