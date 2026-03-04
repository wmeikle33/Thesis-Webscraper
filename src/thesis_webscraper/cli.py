from __future__ import annotations

from pathlib import Path
import json
import typer
from rich import print
from rich.console import Console

from scraper import scrape
from thesis_webscraper.config import ScrapeConfig

app = typer.Typer(add_completion=False, help="Thesis Webscraper CLI")
console = Console()

@app.command()
def run(
    config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True, help="Path to config JSON/YAML"),
    out_dir: Path = typer.Option(Path("data"), "--out-dir", "-o", help="Output directory"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser headless"),
    max_pages: int = typer.Option(0, "--max-pages", help="0 means no limit"),
    delay_min: float = typer.Option(1.0, "--delay-min", help="Min delay between actions (seconds)"),
    delay_max: float = typer.Option(3.0, "--delay-max", help="Max delay between actions (seconds)"),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume from checkpoint if present"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """
    Run the scraper using a config file and write outputs to out_dir.
    Produces posts.csv, comments.csv, run_metadata.json (and optionally checkpoints).
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = ScrapeConfig.from_file(config)
    cfg.headless = headless
    cfg.max_pages = max_pages or None
    cfg.delay_min = delay_min
    cfg.delay_max = delay_max
    cfg.resume = resume
    cfg.verbose = verbose
    cfg.out_dir = out_dir

    result = scrape(cfg)

    # Print a human-friendly summary
    print("[bold green]Done![/bold green]")
    print(f"Posts: {result.posts_count}")
    print(f"Comments: {result.comments_count}")
    print(f"Output: {out_dir.resolve()}")

    # Optional: always write a machine-readable summary
    (out_dir / "run_summary.json").write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")


@app.command()
def validate(
    config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True),
):
    """Validate config and environment (drivers, credentials presence, etc.)."""
    cfg = ScrapeConfig.from_file(config)
    problems = cfg.validate_environment()
    if problems:
        print("[bold red]Validation failed:[/bold red]")
        for p in problems:
            print(f"- {p}")
        raise typer.Exit(code=2)
    print("[bold green]Validation OK[/bold green]")


def main():
    app()


if __name__ == "__main__":
    main()
