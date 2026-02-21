# thesis_webscraper/settings.py
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env into process env if present

@dataclass
class Settings:
    start_url: str = "https://example.com"
    pages: int = 10
    headless: bool = True
    delay_ms: int = 500
    jitter_ms: int = 300
    out_path: str = "data/output.parquet"
    log_jsonl: str = "logs/scraper.jsonl"

    @classmethod
    def from_env(cls) -> "Settings":
        def as_bool(v, default):
            if v is None: return default
            return v.lower() in {"1", "true", "yes", "y", "on"}
        return cls(
            start_url=os.getenv("START_URL", cls.start_url),
            pages=int(os.getenv("PAGES", cls.pages)),
            headless=as_bool(os.getenv("HEADLESS"), cls.headless),
            delay_ms=int(os.getenv("DELAY_MS", cls.delay_ms)),
            jitter_ms=int(os.getenv("JITTER_MS", cls.jitter_ms)),
            out_path=os.getenv("OUT_PATH", cls.out_path),
            log_jsonl=os.getenv("LOG_JSONL", cls.log_jsonl),
        )
