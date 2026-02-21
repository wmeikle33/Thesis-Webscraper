from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())

def run(query: str, limit: int = 100) -> None:
    # TODO: call your existing scraping pipeline here
    print(f"Running scraper with query={query}, limit={limit}")
