
"""
Chinese stopword utilities for Thesis-Webscraper.

Features:
- Load stopwords from text files
- Combine default and custom stopwords
- Preserve important domain-specific words
- Filter tokenized Chinese text
- Filter DataFrame columns
- Generate removal statistics
- Save stopword dictionaries

Stopword removal is intended primarily for
keyword extraction, TF-IDF, and topic analysis.

Avoid removing stopwords before sentiment
analysis unless the model explicitly requires it.
"""

from pathlib import Path
from collections.abc import Iterable

import jieba
import pandas as pd


# Small conservative baseline.
DEFAULT_STOPWORDS = {
    "的",
    "了",
    "着",
    "和",
    "与",
    "及",
    "或",
    "而",
    "在",
    "是",
    "有",
    "这",
    "那",
    "这个",
    "那个",
    "这些",
    "那些",
    "一个",
    "一些",
    "我们",
    "你们",
    "他们",
    "它们",
    "自己",
    "我",
    "你",
    "他",
    "她",
    "它",
    "啊",
    "呀",
    "呢",
    "吧",
    "哦",
    "吗",
    "啦",
}


# Important words that should generally
# remain available for EV topic analysis.
DOMAIN_TERMS = {
    "电池",
    "续航",
    "充电",
    "快充",
    "价格",
    "安全",
    "质量",
    "性能",
    "动力",
    "驾驶",
    "比亚迪",
    "特斯拉",
    "蔚来",
    "小鹏",
    "理想汽车",
    "BYD",
    "Tesla",
    "NIO",
}


# Negation and intensity words should
# generally be preserved for sentiment.
SENTIMENT_TERMS = {
    "不",
    "没",
    "没有",
    "不是",
    "非常",
    "特别",
    "很",
    "太",
    "比较",
    "有点",
    "好",
    "差",
    "满意",
    "失望",
}


def load_stopwords(
    file_path: str | Path,
) -> set[str]:
    """
    Load stopwords from a UTF-8 text file.

    Expected format:
        One stopword per line.

    Blank lines and lines beginning with #
    are ignored.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        words = {
            line.strip()
            for line in file
            if line.strip()
            and not line.lstrip().startswith("#")
        }

    return words


def get_default_stopwords() -> set[str]:
    """
    Return a copy of the default dictionary.
    """

    return DEFAULT_STOPWORDS.copy()


def build_stopword_set(
    custom_stopwords: Iterable[str] | None = None,
    stopword_file: str | Path | None = None,
    preserve_domain_terms: bool = True,
    preserve_sentiment_terms: bool = True,
    additional_preserved: Iterable[str] | None = None,
) -> set[str]:
    """
    Build the effective stopword dictionary.

    Combines defaults, custom words, and
    optional file-based stopwords.
    """

    stopwords = get_default_stopwords()

    if custom_stopwords is not None:
        stopwords.update(custom_stopwords)

    if stopword_file is not None:
        stopwords.update(
            load_stopwords(stopword_file)
        )

    protected = set()

    if preserve_domain_terms:
        protected.update(DOMAIN_TERMS)

    if preserve_sentiment_terms:
        protected.update(SENTIMENT_TERMS)

    if additional_preserved is not None:
        protected.update(additional_preserved)

    return stopwords - protected


def remove_stopwords(
    tokens: Iterable[str],
    stopwords: set[str] | None = None,
    remove_empty: bool = True,
) -> list[str]:
    """
    Remove stopwords from a token sequence.

    Preserves the original token order.
    """

    if stopwords is None:
        stopwords = build_stopword_set()

    result = []

    for token in tokens:
        token = token.strip()

        if remove_empty and not token:
            continue

        if token in stopwords:
            continue

        result.append(token)

    return result


def filter_text_stopwords(
    text: str,
    stopwords: set[str] | None = None,
) -> list[str]:
    """
    Tokenize Chinese text and remove stopwords.

    Returns a list of tokens rather than
    reconstructing the original sentence.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    tokens = jieba.lcut(text)

    return remove_stopwords(
        tokens,
        stopwords=stopwords,
    )


def remove_stopwords_dataframe(
    df: pd.DataFrame,
    text_column: str = "normalized_text",
    output_column: str = "filtered_tokens",
    stopwords: set[str] | None = None,
) -> pd.DataFrame:
    """
    Tokenize and filter an entire DataFrame.

    The original text column is preserved.
    """

    if text_column not in df.columns:
        raise KeyError(
            f"Missing column: {text_column}"
        )

    if stopwords is None:
        stopwords = build_stopword_set()

    result = df.copy()

    result[output_column] = (
        result[text_column].apply(
            lambda text: filter_text_stopwords(
                text,
                stopwords=stopwords,
            )
        )
    )

    return result


def stopword_removal_summary(
    original_tokens: Iterable[str],
    filtered_tokens: Iterable[str],
) -> dict:
    """
    Summarize the number of removed tokens.
    """

    original = list(original_tokens)
    filtered = list(filtered_tokens)

    original_count = len(original)
    filtered_count = len(filtered)

    removed_count = original_count - filtered_count

    return {
        "original_token_count": original_count,
        "filtered_token_count": filtered_count,
        "removed_token_count": removed_count,
        "removal_rate": (
            removed_count / original_count
            if original_count
            else 0.0
        ),
    }


def save_stopwords(
    stopwords: Iterable[str],
    file_path: str | Path,
) -> None:
    """
    Save stopwords as a sorted UTF-8 text file.
    """

    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for word in sorted(set(stopwords)):
            file.write(f"{word}\n")

