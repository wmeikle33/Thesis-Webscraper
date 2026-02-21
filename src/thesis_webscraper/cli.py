import typer
from typing import Optional
from .settings import Settings
from .scraper import run_scrape

app = typer.Typer(add_completion=False)

@app.callback(no_args_is_help=True)
def main():
    """Thesis Webscraper — CLI + .env config"""

@app.command()
def scrape(
    start_url: Optional[str] = typer.Option(None, help="Start URL"),
    pages: Optional[int] = typer.Option(None, help="Number of pages to crawl"),
    headless: Optional[bool] = typer.Option(None, help="Run browser headless"),
    delay_ms: Optional[int] = typer.Option(None, help="Base delay (ms) between actions"),
    jitter_ms: Optional[int] = typer.Option(None, help="Random jitter (ms) added to delay"),
    out_path: Optional[str] = typer.Option(None, help="Output file (.parquet/.csv)"),
    log_jsonl: Optional[str] = typer.Option(None, help="Structured log file"),
):
    """
    Run the scraper. CLI options override .env and defaults.
    """
    s = Settings()  # loads .env automatically (pydantic) or Settings.from_env() if dataclass
    # Override with CLI if provided
    if start_url is not None: s.start_url = start_url
    if pages is not None: s.pages = pages
    if headless is not None: s.headless = headless
    if delay_ms is not None: s.delay_ms = delay_ms
    if jitter_ms is not None: s.jitter_ms = jitter_ms
    if out_path is not None: s.out_path = out_path
    if log_jsonl is not None: s.log_jsonl = log_jsonl

    typer.echo(f"[config] {s}")
    run_scrape(s)

def run():
    app()

if __name__ == "__main__":
    run()
