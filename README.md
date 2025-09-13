# Thesis Webscraper
  This is my code for the master's thesis. Specifically, this code was used to collect blog post texts from the website Autohome, one of the leading sites for automobile consumers in China.The premise of my thesis is write a web scraping program that collects consumer posted blog content from Chinese websites pertaining to foreign made EV models currently available in the Chinese market. Specifically, the title of the blog post was collected, the main body content as well as the comments. I then measure how many times certain words associated with EV adoption are mentioned in this text, using the findings to generate a principal component regression vis a visa company stock returns to provide an assessmenet and general market insight of the potential of the Chinese EV market for foreign companes. Specifically, after the principal component regressionw as completed, the text valuues for with the highest eigenvectors for each principal component were extracted. Based on these text values, it was then determined which factors affecting EV adoption were the most important for Chinese consumers. Below is a graph depicting the various categories of text variables that were used in the analysis. 



<img width="478" height="596" alt="Screenshot 2025-09-08 at 8 17 46 PM" src="https://github.com/user-attachments/assets/f726ed40-30c0-401e-88f4-764f857b3c01" />

It should be noted that this project was developed using Selenium 3.141.0. Update to Selenium 4+ requires migration of element selection methods.

Usage
This project is a Selenium-based scraper used for a master’s thesis to collect blog posts (title/body/comments) from Autohome (and similar sites) and write them to disk for downstream analysis.
Heads-up: The original project targeted Selenium 3. If you’re on Selenium 4, use By.* locators and explicit waits. See the Troubleshooting section.
Quick start
# 1) Clone and enter the project
git clone https://github.com/wmeikle33/Thesis-Webscraper.git
cd Thesis-Webscraper

# 2) Create & activate a virtual environment (Python 3.10+ recommended)
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (Powershell)
.venv\Scripts\Activate.ps1

# 3) Install dependencies
pip install -U pip
pip install -r requirements.txt

# 4) (Optional) Create a .env to configure polite crawling & output paths
cp .env.example .env  # then edit .env

# 5) Run a short scrape in headless mode
python -m src.main --start-url "https://example.com/list" --pages 3 --out data/autohome.parquet
If your entry point isn’t src/main.py, replace the command accordingly (e.g., python -m src.scraper or python src/main.py ...).
Requirements
Python: 3.10 or newer
Browser: Chrome/Chromium, Edge, or Firefox
Selenium 4 (recommended): Selenium Manager can auto-install a compatible driver.
Internet access and permission to scrape the target site(s).
If you must stay on Selenium 3, you’ll need a matching WebDriver binary on PATH. Selenium 4 removes the old find_element_by_* APIs.
Configuration
You can configure most behavior via CLI flags or a .env file. The repo includes a sample:
.env.example
# Politeness / performance
REQUEST_DELAY_MS=1200        # base delay between requests
RANDOM_JITTER=0.4            # add ±40% jitter to delays
MAX_RETRIES=2                # retry list/detail fetches
HEADLESS=1                   # 1=headless, 0=headed
BROWSER=chrome               # chrome|edge|firefox

# Targeting
START_URL=https://example.com/list
PAGES=10

# Output
OUTPUT_PATH=data/autohome.parquet
SAVE_RAW_HTML=0              # 1 to also save raw HTML per page (debug)

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/scraper.jsonl
Environment variables are optional—everything can be passed as flags.
Running
Basic scrape
python -m src.main \
  --start-url "https://example.com/list" \
  --pages 50 \
  --out data/autohome.parquet \
  --headless 1 \
  --delay-ms 1200 \
  --jitter 0.4
From a list of detail URLs (CSV/JSONL)
If you already have a file of post URLs:
python -m src.main \
  --urls-file data/urls.csv \
  --out data/autohome.parquet
Common flags
Flag	Type	Default	Description
--start-url	str	required*	List page to begin crawling (ignored if --urls-file is used)
--pages	int	1	Number of list pages to traverse
--urls-file	path	—	CSV/JSONL file containing url column/field
--out	path	data/autohome.parquet	Output file (Parquet or CSV by extension)
--headless	0/1	1	Run the browser headless
--browser	str	chrome	chrome, edge, or firefox
--delay-ms	int	1200	Base politeness delay between requests
--jitter	float	0.4	Random ±jitter multiplier on delay
--max-retries	int	2	Retries on transient failures
--save-raw-html	0/1	0	Save raw page HTML alongside parsed data
--log-file	path	logs/scraper.jsonl	Rotating JSONL log file
--log-level	str	INFO	DEBUG, INFO, WARNING, ERROR
*If no --start-url is provided, the script will read it from START_URL in .env.
Outputs
By default the scraper writes a Parquet file (recommended) or CSV if --out ends with .csv.
Suggested schema (example):
Column	Type	Notes
url	string	canonical detail URL
post_id	string	extracted identifier, if available
title	string	text
body_html	string	raw HTML of post body (optional)
body_text	string	cleaned text
author	string	if available
created_at	datetime	parsed timestamp, if available
comments_count	int	if available
language	string	e.g., zh
scraped_at	datetime	UTC timestamp
If --save-raw-html=1, raw HTML files will be stored under data/raw/ mirroring the URL/path.
Logging
The scraper writes newline-delimited JSON logs (easy to grep/index) and a human console stream.
Typical events:
run_start, run_end (with total rows and duration)
navigate (URL, page_no)
list_parsed (items_found)
detail_parsed (url, text_len)
saved (path, rows_written)
*_failed with exception info (and optional screenshot path)
Change the file via --log-file or LOG_FILE. Rotate/retention may be handled by the logger config in code.
Reproducibility & politeness
Use HEADLESS=1, delays, and jitter to avoid hammering servers.
Keep concurrency = 1 (default).
Record your software versions (Python, Selenium, browser) in your run logs.
For academic publications, document scrape window, frequency, and filters.
Testing (optional)
If you add tests using saved HTML fixtures:
pip install -r requirements-dev.txt  # if you keep dev deps separate
pytest -q
Unit tests should feed stored HTML into your parse functions (no live web access) to make CI reliable.
Troubleshooting
I get AttributeError: 'WebDriver' object has no attribute 'find_element_by_*'
You’re on Selenium 4. Replace legacy calls like:
# old (Selenium 3)
el = driver.find_element_by_css_selector("div.post-content")
with:
# new (Selenium 4)
from selenium.webdriver.common.by import By
el = driver.find_element(By.CSS_SELECTOR, "div.post-content")
Use explicit waits:
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20)
el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.post-content")))
“No such driver” or driver mismatch
With Selenium 4, Selenium Manager usually installs the correct driver automatically. Ensure your browser is installed and up to date. You can also pin a browser channel (e.g., stable) or switch browsers with --browser.
Headless mode renders differently
Some pages behave differently headless. Try --headless 0 and increase waits.
Captcha / blocking
Back off (increase --delay-ms and --jitter), run during lower-traffic hours, reduce pages per run, and comply with site rules.
Encoding / text is garbled
Ensure you decode content as UTF-8; for Chinese text, verify fonts/locales if you later render plots. Consider storing both body_html and a cleaned body_text.
Ethics & compliance (summary)
Respect Terms of Service and robots.txt of the target site(s).
This project is intended for academic research and should not be used for unlawful purposes.
Avoid collecting PII; publish only aggregated/anonymized results.
Use reasonable rate limits; do not run high-concurrency scrapes.
See the main README’s Ethics & Compliance section for fuller guidance.
FAQ
Q: Can I resume from where I left off?
A: Keep a record of the last processed page/post ID and skip already-seen items (simple approach: store a hash of url+title+timestamp). Add a --resume flag if you implement this.
Q: CSV or Parquet?
A: Prefer Parquet (--out data/autohome.parquet) for speed and smaller size; it preserves types.
Q: Which browser is best?
A: Chrome with Selenium Manager is the default/easiest. Firefox works too; switch with --browser firefox.
Citation
If you use this code or dataset in academic work, please cite the repository and describe your collection window and methodology.


# Ethics & Compliance

Legal & Terms of Service

This code was developed for academic research (Master’s thesis) and is provided for educational purposes only.
Before running the scraper, check and comply with the Terms of Service (ToS) and robots.txt of the target website(s).
The authors do not encourage scraping in violation of site policies or applicable laws.

Politeness & Fair Use

The scraper introduces delays between requests to avoid overloading servers.
Please configure reasonable backoff intervals (e.g., 1–2 seconds per request).
Do not run high-concurrency scraping or large-scale crawls against Autohome or other sites.

Data Privacy

Scraped content may include user-generated data such as comments, usernames, and timestamps.
This project does not attempt to deanonymize users or collect personally identifiable information (PII).
Any analysis or publication of results should use aggregated and anonymized data only.

Transparency & Attribution

When sharing or publishing results derived from scraped data:
Cite the source site clearly.
Describe your data collection window and methods (e.g., frequency, filters).
Acknowledge the limitations and ethical considerations.

Responsible Use

Do not use this project for:
Commercial resale of scraped data
Mass harvesting of user profiles
Activities that violate privacy, local laws, or data protection regulations (e.g., GDPR)

Disclaimer: This scraper was built solely for academic research into EV adoption trends (Master’s thesis, 2023). The authors do not endorse or permit the use of this code for unlawful purposes. By using this repository, you agree to ensure your usage complies with relevant laws, data protection standards, and the Terms of Service of the websites you access.
