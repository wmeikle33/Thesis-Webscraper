# Overview 

## What this project does

This project scrapes text data from the Chinese website Autohome for thesis research. Collecting information by hand can be very time consuming. On the other hand, scraping data online provides a much faster alternative method of data collection. To this end, this project uses a web scraping methodology to collect text data before scanning it for specific key words. These key words are then incorporated in a Principal Component Regression Analysis vis a vis company stock returns to measure which text variables were positively correlated with company performance. It uses Selenium to load target pages, extracts structured post and comment text, normalizes the data into tabular form, and writes the results to local files for downstream analysis. The repository is organized as a small Python package with a CLI, tests, and documentation.

```md
## Scraping pipeline

```mermaid
flowchart TD
    A[Input: list page URLs] --> B[Load dynamic pages with Selenium]
    B --> C[Parse list pages]
    C --> D[Collect thread/detail links]
    D --> E[Scrape detail pages]
    E --> F[Extract post-level data]
    E --> G[Extract comment-level data]
    F --> H[Normalize schema]
    G --> H
    H --> I[Deduplicate by IDs / keys]
    I --> J[posts.csv]
    I --> K[comments.csv]
    I --> L[run_metadata.json]
    P --> Q[clean text]
    Q --> R[tokenize]
    R --> S[sentiment analysis]
    S --> T[keyword analysis]
    T --> U[feature matrix generation] 

```

# Quickstart

### Prerequisites
- Python 3.10+
- Chrome/Chromium (Selenium will use it)

For full instructions on how to run the scraper, configuration options, and examples, see:
➡️ [Usage Guide](USAGE.md)

## Configuration

Copy `.env.example` to `.env` and update values as needed:

```bash
cp .env.example .env

### Install
```bash
git clone https://github.com/wmeikle33/Thesis-Webscraper.git
cd Thesis-Webscraper
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
pip install -e .[dev]
thesis-webscraper --help

```

```bash

thesis-webscraper run \
  --section used-cars \
  --pages 10 \
  --out-dir data \
  --headless \
  --delay-ms 1200 \
  --jitter 0.4 \
  --max-retries 2 \
  --resume \
  --verbose

```

## How it works

1. **List page parsing**  
   The scraper opens forum or listing pages and collects candidate post URLs.

2. **Detail page parsing**  
   Each post page is loaded in Selenium, and the scraper extracts post-level fields and any visible comments.

3. **Deduplication and normalization**  
   Records are normalized into a stable schema, keyed by post and comment identifiers to reduce duplicate rows.

4. **Output writing**  
   Structured records are written to CSV, and run metadata is saved for traceability and reproducibility.\

## What it outputs

After a successful run, the scraper writes data to:
./data/ (default output directory)
posts.csv — forum post-level data
comments.csv — comment-level data (if applicable)
run_metadata.json — run info (timestamp, args, counts, errors)

# Schema

## posts.csv

```bash

post_id (string) — unique ID (from URL or page)
url (string)
title (string, UTF-8)
body (string, UTF-8)
author (string)
created_at (string / ISO timestamp if available)
scraped_at (string / ISO timestamp)
source (string) — e.g., autohome

```

## comments.csv

```bash

post_id (string) — foreign key to posts.csv
comment_id (string)
comment_text (string, UTF-8)
comment_author (string)
comment_created_at (string)
scraped_at (string)

```

## Repository Structure

The project is organized into the following directories:

## Repository structure

```text
.
├── .github/workflows/   # CI configuration
├── data/                # Output data and sample artifacts
├── docs/                # Additional project documentation
├── src/                 # Python package source code
├── tests/               # Automated tests and fixtures
├── notebooks/    
├── Changelog.md
├── LICENSE
├── MIGRATING.md
├── README.md
├── USAGE.md
└── pyproject.toml

```
## Quality checks

GitHub Actions CI runs on pushes to `main` and pull requests and currently covers:

- Ruff linting (`ruff check .`)
- Ruff formatting check (`ruff format --check .`)
- Unit tests with `pytest`
- Package build validation (`python -m build`)
- Package metadata validation (`python -m twine check dist/*`)

The workflow runs on Python 3.10, 3.11, and 3.12.
