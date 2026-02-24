from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import os
from typing import Any

@dataclass
class ScrapeConfig:
    base_url: str
    username_env: str = "SCRAPER_USERNAME"
    password_env: str = "SCRAPER_PASSWORD"
    headless: bool = True
    max_pages: int | None = None
    delay_min: float = 1.0
    delay_max: float = 3.0
    resume: bool = True
    verbose: bool = False
    out_dir: Path = Path("data")

    @staticmethod
    def from_file(path: Path) -> "ScrapeConfig":
        data = json.loads(path.read_text(encoding="utf-8"))
        return ScrapeConfig(**data)

    def validate_environment(self) -> list[str]:
        problems: list[str] = []
        if not os.getenv(self.username_env):
            problems.append(f"Missing env var: {self.username_env}")
        if not os.getenv(self.password_env):
            problems.append(f"Missing env var: {self.password_env}")
        # Add checks like chrome/driver presence if you can detect them safely.
        return problems
