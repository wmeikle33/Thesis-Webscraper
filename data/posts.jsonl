import json
from datetime import datetime, timezone
from pathlib import Path

def write_jsonl(path: str, record: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
