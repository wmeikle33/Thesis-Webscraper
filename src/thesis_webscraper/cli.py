# src/thesis_webscraper/cli.py
from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print
from thesis_webscraper.config import SECTION_URLS
from thesis_webscraper.config import ScrapeConfig
from scraping.crawler import scrape

app = typer.Typer(add_completion=False, help="Thesis Webscraper CLI")

@app.command("sections")
def sections():
    for name in SECTION_URLS:
        print(name)

@app.command()
def run(
    section: str = typer.Option(..., "--section", help="Autohome section to scrape"),
    pages: int = typer.Option(1, "--pages", min=1, help="Number of list pages to crawl"),
    out_dir: Path = typer.Option(Path("data/"), "--out-dir", help="Output file path"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
    delay_ms: int = typer.Option(1200, "--delay-ms", min=0, help="Base delay between requests in ms"),
    jitter: float = typer.Option(0.4, "--jitter", min=0.0, help="Random jitter multiplier"),
    max_retries: int = typer.Option(2, "--max-retries", min=0, help="Retries for transient failures"),
    save_raw_html: bool = typer.Option(False, "--save-raw-html/--no-save-raw-html", help="Save raw HTML"),
    resume: bool = typer.Option(False, "--resume/--no-resume", help="Resume from prior checkpoint"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    cfg = ScrapeConfig(
        section=section,
        pages=pages,
        out_dir=out_dir,
        headless=headless,
        delay_ms=delay_ms,
        jitter=jitter,
        max_retries=max_retries,
        save_raw_html=save_raw_html,
        resume=resume,
        verbose=verbose,
    )

    result = scrape(cfg)

    print("[bold green]Done![/bold green]")
    print(f"Posts: {result.posts_count}")
    print(f"Comments: {result.comments_count}")
    print(f"Output: {out_dir.resolve()}")

    summary_path = out_dir.parent / "run_summary.json"
    summary_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")


def main():
    app()


if __name__ == "__main__":
    main()
