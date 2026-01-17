def load_seen(path: str) -> set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    return set(line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip())

def mark_seen(path: str, url: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(url + "\n")
