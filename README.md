# Quickstart

### Prerequisites
- Python 3.10+
- Chrome/Chromium (Selenium will use it)

For full instructions on how to run the scraper, configuration options, and examples, see:
➡️ [Usage Guide](USAGE.md)

### Install
```bash
git clone https://github.com/wmeikle33/Thesis-Webscraper.git
cd Thesis-Webscraper
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
thesis-webscraper --help

```

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

```bash
.
├── src/            # Source code for the application
├── docs/           # Project documentation and guides
├── tests/           # Automated tests (unit, integration)
├── build/          # Compiled output files (usually excluded from git)
├── .github/        # GitHub specific configurations (workflows, templates)
├── LICENSE         # Project license file
└── README.md       # The main information file (this file)
```

