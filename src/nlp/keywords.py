
"""
Keyword extraction for Thesis-Webscraper.

Extract and analyze Chinese automotive forum keywords.

Supports:
- Dictionary-based keyword matching
- Keyword counts and topic categories
- Keyword density
- TF-IDF extraction
- Temporal keyword aggregation
"""

from collections import Counter
from collections.abc import Mapping, Sequence

import jieba
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)


EV_KEYWORDS = {
    "battery": [
        "电池",
        "电池寿命",
        "电池容量",
        "刀片电池",
        "固态电池",
    ],
    "range": [
        "续航",
        "续航里程",
        "里程焦虑",
        "能耗",
    ],
    "charging": [
        "充电",
        "快充",
        "充电桩",
        "充电速度",
        "超充",
    ],
    "price": [
        "价格",
        "售价",
        "降价",
        "性价比",
        "补贴",
    ],
    "safety": [
        "安全",
        "碰撞",
        "自燃",
        "刹车",
        "事故",
    ],
    "performance": [
        "加速",
        "动力",
        "操控",
        "马力",
        "扭矩",
    ],
    "technology": [
        "自动驾驶",
        "智能驾驶",
        "辅助驾驶",
        "车机",
        "智能座舱",
    ],
    "quality": [
        "质量",
        "故障",
        "维修",
        "售后",
        "做工",
    ],
}


def tokenize_for_keywords(
    text: str,
) -> list[str]:
    """
    Segment Chinese text into tokens.
    """

    if not isinstance(text, str):
        return []

    return [
        token.strip()
        for token in jieba.lcut(text)
        if token.strip()
    ]


def extract_keywords(
    text: str,
    keywords: Sequence[str],
) -> list[str]:
    """
    Return dictionary keywords found in a post.

    Matching uses literal substring search.
    Each keyword appears at most once in output.
    """

    if not isinstance(text, str):
        return []

    return [
        keyword
        for keyword in dict.fromkeys(keywords)
        if keyword and keyword in text
    ]


def count_keywords(
    text: str,
    keywords: Sequence[str],
) -> dict[str, int]:
    """
    Count occurrences of each keyword.

    Counts are non-overlapping for each keyword.
    Different keywords may overlap.
    """

    if not isinstance(text, str):
        text = ""

    return {
        keyword: text.count(keyword)
        for keyword in dict.fromkeys(keywords)
        if keyword
    }


def extract_keyword_categories(
    text: str,
    keyword_dict: Mapping[
        str, Sequence[str]
    ] | None = None,
) -> dict[str, int]:
    """
    Count keyword occurrences for each EV topic.

    Returns one count per category.
    """

    if keyword_dict is None:
        keyword_dict = EV_KEYWORDS

    result = {}

    for category, keywords in keyword_dict.items():
        counts = count_keywords(text, keywords)

        result[category] = sum(counts.values())

    return result


def calculate_keyword_frequencies(
    df: pd.DataFrame,
    text_column: str = "cleaned_text",
    keyword_dict: Mapping[
        str, Sequence[str]
    ] | None = None,
) -> pd.DataFrame:
    """
    Generate topic count features for each post.

    Returns a DataFrame with the same index as df.
    """

    if text_column not in df.columns:
        raise KeyError(
            f"Missing column: {text_column}"
        )

    if keyword_dict is None:
        keyword_dict = EV_KEYWORDS

    records = [
        extract_keyword_categories(
            text,
            keyword_dict,
        )
        for text in df[text_column].fillna("")
    ]

    result = pd.DataFrame(
        records,
        index=df.index,
        columns=list(keyword_dict),
    )

    return result.fillna(0).astype(int).add_prefix(
        "keyword_"
    )


def calculate_keyword_density(
    df: pd.DataFrame,
    text_column: str = "cleaned_text",
    keyword_dict: Mapping[
        str, Sequence[str]
    ] | None = None,
) -> pd.DataFrame:
    """
    Calculate keyword counts per 100 characters.

    Uses total text length as the denominator.
    """

    frequencies = calculate_keyword_frequencies(
        df,
        text_column=text_column,
        keyword_dict=keyword_dict,
    )

    lengths = (
        df[text_column]
        .fillna("")
        .astype(str)
        .str.len()
        .replace(0, np.nan)
    )

    densities = (
        frequencies.div(lengths, axis=0) * 100
    )

    return densities.fillna(0).add_suffix(
        "_density"
    )


def extract_tfidf_keywords(
    texts: Sequence[str],
    max_features: int = 100,
    top_n: int = 20,
) -> pd.DataFrame:
    """
    Extract the highest average TF-IDF terms
    across a collection of Chinese documents.

    Intended for exploratory vocabulary analysis.
    """

    documents = [
        text if isinstance(text, str) else ""
        for text in texts
    ]

    if not documents:
        return pd.DataFrame(
            columns=["keyword", "tfidf_score"]
        )

    vectorizer = TfidfVectorizer(
        tokenizer=tokenize_for_keywords,
        token_pattern=None,
        lowercase=False,
        max_features=max_features,
    )

    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError as exc:
        if "empty vocabulary" in str(exc):
            return pd.DataFrame(
                columns=["keyword", "tfidf_score"]
            )
        raise

    scores = np.asarray(
        matrix.mean(axis=0)
    ).ravel()

    keywords = vectorizer.get_feature_names_out()

    result = pd.DataFrame({
        "keyword": keywords,
        "tfidf_score": scores,
    })

    return (
        result.sort_values(
            "tfidf_score",
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def aggregate_keyword_trends(
    df: pd.DataFrame,
    date_column: str = "created_at",
    frequency: str = "D",
    group_column: str | None = "brand",
) -> pd.DataFrame:
    """
    Aggregate keyword counts by date and
    optionally by brand.

    Expects keyword_* count columns.
    """

    if date_column not in df.columns:
        raise KeyError(
            f"Missing date column: {date_column}"
        )

    keyword_columns = [
        column
        for column in df.columns
        if column.startswith("keyword_")
        and not column.endswith("_density")
    ]

    if not keyword_columns:
        raise ValueError("No keyword count columns found")

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce",
    )

    data = data.dropna(subset=[date_column])

    data["_period"] = (
        data[date_column]
        .dt.to_period(frequency)
        .dt.to_timestamp()
    )

    group_columns = ["_period"]

    if group_column is not None:
        if group_column not in data.columns:
            raise KeyError(
                f"Missing group column: {group_column}"
            )

        group_columns.append(group_column)

    result = (
        data.groupby(
            group_columns,
            as_index=False,
        )[keyword_columns]
        .sum()
    )

    return result.rename(
        columns={"_period": "period"}
    )


def get_top_keywords(
    texts: Sequence[str],
    top_n: int = 20,
    stopwords: set[str] | None = None,
) -> pd.DataFrame:
    """
    Return the most frequent Chinese tokens.

    Useful for discovering new vocabulary
    to add to EV_KEYWORDS.
    """

    if stopwords is None:
        stopwords = set()

    counter = Counter()

    for text in texts:
        tokens = tokenize_for_keywords(text)

        counter.update(
            token
            for token in tokens
            if token not in stopwords
            and len(token) > 1
        )

    return pd.DataFrame(
        counter.most_common(top_n),
        columns=["keyword", "frequency"],
    )

