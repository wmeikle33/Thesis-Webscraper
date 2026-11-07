from __future__ import annotations

import hashlib
import re
from bs4 import BeautifulSoup

from .models import CommentRecord, PostRecord


def extract_post_id(url: str) -> str:
    # Try a URL-based ID first, fallback to hash
    m = re.search(r"/bbs/thread/([A-Za-z0-9_-]+)", url)
    if m:
        return m.group(1)
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def make_comment_id(post_id: str, text: str, index: int) -> str:
    raw = f"{post_id}|{index}|{text.strip()}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def parse_post(html: str, url: str) -> tuple[PostRecord, list[CommentRecord]]:
    soup = BeautifulSoup(html, "html.parser")

    post_id = extract_post_id(url)

    title_el = soup.select_one(".post-title")
    body_el = soup.select_one(".tz-paragraph")
    author_el = soup.select_one(".post-author")
    created_el = soup.select_one(".post-time")

    post = PostRecord(
        post_id=post_id,
        url=url,
        title=title_el.get_text(strip=True) if title_el else "",
        body=body_el.get_text("\n", strip=True) if body_el else "",
        author=author_el.get_text(strip=True) if author_el else None,
        created_at=created_el.get_text(strip=True) if created_el else None,
    )

    comments: list[CommentRecord] = []

    comment_nodes = soup.select(".reply-detail")
    for idx, node in enumerate(comment_nodes, start=1):
        text = node.get_text(" ", strip=True)
        if not text:
            continue

        comments.append(
            CommentRecord(
                comment_id=make_comment_id(post_id, text, idx),
                post_id=post_id,
                comment_text=text,
            )
        )

    return post, comments
