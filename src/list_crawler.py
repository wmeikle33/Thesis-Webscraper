from bs4 import BeautifulSoup
from .models import Post

def parse_post(html: str, url: str) -> Post:
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one(".post-title")
    title = title_el.get_text(strip=True) if title_el else ""

    body_el = soup.select_one(".tz-paragraph")
    body = body_el.get_text("\n", strip=True) if body_el else ""

    comments = [el.get_text(strip=True) for el in soup.select(".reply-detail")]
    subcomments = [el.get_text(strip=True) for el in soup.select(".reply-sub-front")]

    # optional: remove empties
    comments = [c for c in comments if c]
    subcomments = [c for c in subcomments if c]

    return Post(
        url=url,
        title=title,
        body=body,
        comments=comments,
        subcomments=subcomments,
    )
