from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Post:
    url: str
    title: str
    body: str
    comments: List[str]
    subcomments: List[str]
    scraped_at: Optional[str] = None
