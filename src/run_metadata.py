from __future__ import annotations

import json
import platform
import sys
import time
import traceback
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_git_commit_hash() -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return None


def safe_pkg_version(dist_name: str) -> Optional[str]:
    try:
        from importlib.metadata import version
        return version(dist_name)
    except Exception:
        return None


@dataclass
class StageTiming:
    seconds: float = 0.0


@dataclass
class RunMetadata:
    # Identity
    run_id: str
    started_at_utc: str = field(default_factory=utc_now_iso)
    finished_at_utc: Optional[str] = None
    status: str = "running"  # running|success|failed|partial

    # Reproducibility
    args: Dict[str, Any] = field(default_factory=dict)
    git_commit: Optional[str] = field(default_factory=get_git_commit_hash)

    # Environment
    environment: Dict[str, Any] = field(default_factory=dict)

    # Counts / outcomes
    counts: Dict[str, int] = field(default_factory=lambda: {
        "pages_visited": 0,
        "posts_parsed": 0,
        "comments_parsed": 0,
        "urls_discovered": 0,
        "urls_enqueued": 0,
        "urls_completed": 0,
        "urls_failed": 0,
    })
    failures_by_type: Dict[str, int] = field(default_factory=dict)

    # Timing per stage
    timings: Dict[str, StageTiming] = field(default_factory=lambda: {
        "discover_urls": StageTiming(),
        "fetch_pages": StageTiming(),
        "parse": StageTiming(),
        "write_outputs": StageTiming(),
    })

    # Artifacts / resume
    artifacts: Dict[str, str] = field(default_factory=dict)
    resume: Dict[str, Any] = field(default_factory=dict)

    # Error details (if any)
    error: Optional[Dict[str, Any]] = None

    def init_environment(self) -> None:
        self.environment = {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "selenium_version": safe_pkg_version("selenium"),
            # Add your browser/driver versions if you can query them at runtime (see below).
        }

    def bump_failure(self, failure_type: str) -> None:
        self.failures_by_type[failure_type] = self.failures_by_type.get(failure_type, 0) + 1

    def save(self, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "run_metadata.json"
        payload = asdict(self)

        # Convert StageTiming objects to dicts
        payload["timings"] = {k: asdict(v) for k, v in self.timings.items()}

        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def finish_success(self) -> None:
        self.status = "success"
        self.finished_at_utc = utc_now_iso()

    def finish_failure(self, exc: BaseException) -> None:
        self.status = "failed"
        self.finished_at_utc = utc_now_iso()
        self.error = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }


class stage_timer:
    """Context manager that accumulates stage time into RunMetadata.timings[stage].seconds"""
    def __init__(self, meta: RunMetadata, stage: str):
        self.meta = meta
        self.stage = stage
        self.t0 = 0.0

    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        dt = time.perf_counter() - self.t0
        if self.stage not in self.meta.timings:
            self.meta.timings[self.stage] = StageTiming()
        self.meta.timings[self.stage].seconds += dt
        return False
