from src.parser import parse_list

def test_parse_list_basic(read_html):
    html = read_html("list_page.html")
    urls = parse_list(html)
    assert urls, "should find at least one detail URL"
    assert len(urls) == len(set(urls)), "no duplicates"
    assert all(u.startswith("http") for u in urls)

# tests/unit/test_rate_limit.py
import time
from src.util import polite_sleep

def test_polite_sleep_jitter(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    polite_sleep(1200, jitter=0.4)
    assert 0.72 <= slept[0] <= 1.68  # seconds
