
"""
Chinese sentiment analysis for Thesis-Webscraper.

Features:
- Dictionary-based sentiment scoring
- Chinese tokenization
- Negation handling
- Intensity modifiers
- Sentiment classification
- DataFrame analysis
- Time-series aggregation

Scores range from -1 to +1.

This is a baseline model, not a pretrained
Chinese sentiment classifier.
"""

from collections.abc import Mapping
from pathlib import Path
import json
import math

import jieba
import numpy as np
import pandas as pd


POSITIVE_WORDS = {
    "好": 1.0,
    "很好": 1.5,
    "优秀": 2.0,
    "不错": 1.0,
    "满意": 1.5,
    "喜欢": 1.5,
    "可靠": 1.5,
    "稳定": 1.0,
    "便宜": 1.0,
    "划算": 1.5,
    "省电": 1.5,
    "舒适": 1.0,
    "方便": 1.0,
    "安全": 1.0,
    "先进": 1.0,
    "快": 0.5,
}

NEGATIVE_WORDS = {
    "差": -1.0,
    "很差": -1.5,
    "糟糕": -2.0,
    "失望": -1.5,
    "不好": -1.0,
    "故障": -1.5,
    "问题": -0.5,
    "昂贵": -1.0,
    "贵": -0.5,
    "危险": -1.5,
    "慢": -0.5,
    "不稳定": -1.5,
    "不满意": -1.5,
    "维修": -0.5,
    "自燃": -2.0,
}

NEGATIONS = {
    "不",
    "没",
    "没有",
    "并不",
    "不是",
    "不太",
}

INTENSIFIERS = {
    "非常": 1.8,
    "特别": 1.5,
    "十分": 1.5,
    "很": 1.3,
    "太": 1.5,
    "比较": 1.2,
    "有点": 0.7,
    "稍微": 0.6,
}

# Punctuation that ends a local sentiment scope.
CLAUSE_BOUNDARIES = {
    "。",
    "！",
    "!",
    "？",
    "?",
    "；",
    ";",
    "，",
    ",",
}


def load_sentiment_lexicon(
    file_path: str | Path,
) -> dict[str, float]:
    """
    Load a JSON dictionary of word -> score.

    Example:
        {"优秀": 2.0, "糟糕": -2.0}
    """

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        lexicon = json.load(file)

    if not isinstance(lexicon, dict):
        raise ValueError("Lexicon must be a JSON object")

    result = {}

    for word, score in lexicon.items():
        if not isinstance(word, str) or not word:
            raise ValueError("Lexicon keys must be words")

        if isinstance(score, bool) or not isinstance(
            score, (int, float)
        ):
            raise ValueError("Sentiment scores must be numeric")

        if not math.isfinite(score):
            raise ValueError("Sentiment scores must be finite")

        result[word] = float(score)

    return result


def build_sentiment_lexicon(
    positive_words: Mapping[str, float] | None = None,
    negative_words: Mapping[str, float] | None = None,
) -> dict[str, float]:
    """
    Combine positive and negative dictionaries.
    """

    positive = (
        POSITIVE_WORDS
        if positive_words is None
        else positive_words
    )

    negative = (
        NEGATIVE_WORDS
        if negative_words is None
        else negative_words
    )

    return {**positive, **negative}


def tokenize_sentiment(
    text: str,
    lexicon: Mapping[str, float] | None = None,
) -> list[str]:
    """
    Tokenize Chinese text while preserving
    sentiment expressions as single tokens.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    if lexicon is None:
        lexicon = build_sentiment_lexicon()

    tokenizer = jieba.Tokenizer()

    special_words = (
        set(lexicon)
        | NEGATIONS
        | set(INTENSIFIERS)
    )

    for word in special_words:
        tokenizer.add_word(word, freq=1000000)

    return [
        token.strip()
        for token in tokenizer.cut(text, HMM=False)
        if token.strip()
    ]


def calculate_sentiment_score(
    text: str,
    lexicon: Mapping[str, float] | None = None,
) -> float:
    """
    Calculate lexicon-based sentiment.

    Basic rules:
    - Positive words contribute positive values
    - Negative words contribute negative values
    - Negations reverse the next sentiment word
    - Intensifiers change the next sentiment weight
    - Clause boundaries reset modifiers

    Returns a score in [-1, 1].
    """

    if lexicon is None:
        lexicon = build_sentiment_lexicon()

    tokens = tokenize_sentiment(text, lexicon)

    if not tokens:
        return 0.0

    total_score = 0.0
    matched_words = 0

    negation_count = 0
    intensity = 1.0

    for token in tokens:

        if token in CLAUSE_BOUNDARIES:
            negation_count = 0
            intensity = 1.0
            continue

        # Exact sentiment phrases take precedence.
        if token in lexicon:
            score = lexicon[token]

            if negation_count % 2 == 1:
                score *= -1

            score *= intensity

            total_score += score
            matched_words += 1

            negation_count = 0
            intensity = 1.0

        elif token in NEGATIONS:
            negation_count += 1

        elif token in INTENSIFIERS:
            intensity *= INTENSIFIERS[token]

    if matched_words == 0:
        return 0.0

    # Normalize average sentiment to [-1, 1].
    average_score = total_score / matched_words

    return float(np.tanh(average_score))


def classify_sentiment(
    score: float,
    positive_threshold: float = 0.2,
    negative_threshold: float = -0.2,
) -> str:
    """
    Convert a sentiment score into a label.
    """

    if not -1 <= score <= 1:
        raise ValueError("Score must be between -1 and 1")

    if not (
        -1 <= negative_threshold
        < positive_threshold <= 1
    ):
        raise ValueError("Invalid sentiment thresholds")

    if score >= positive_threshold:
        return "positive"

    if score <= negative_threshold:
        return "negative"

    return "neutral"


def analyze_sentiment(
    text: str,
    lexicon: Mapping[str, float] | None = None,
) -> dict:
    """
    Return sentiment score and classification.
    """

    score = calculate_sentiment_score(
        text,
        lexicon=lexicon,
    )

    return {
        "sentiment_score": score,
        "sentiment_label": classify_sentiment(score),
    }


def analyze_dataframe(
    df: pd.DataFrame,
    text_column: str = "cleaned_text",
    lexicon: Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """
    Add sentiment scores and labels to a DataFrame.
    """

    if text_column not in df.columns:
        raise KeyError(
            f"Missing column: {text_column}"
        )

    result = df.copy()

    if lexicon is None:
        lexicon = build_sentiment_lexicon()

    scores = result[text_column].apply(
        lambda text: calculate_sentiment_score(
            text,
            lexicon=lexicon,
        )
    )

    result["sentiment_score"] = scores

    result["sentiment_label"] = scores.apply(
        classify_sentiment
    )

    return result


def aggregate_sentiment(
    df: pd.DataFrame,
    date_column: str = "created_at",
    brand_column: str = "brand",
    frequency: str = "D",
) -> pd.DataFrame:
    """
    Aggregate sentiment by brand and period.

    Returns:
    - Average sentiment
    - Sentiment standard deviation
    - Post count
    - Positive share
    - Negative share
    """

    required = {
        date_column,
        brand_column,
        "sentiment_score",
        "sentiment_label",
    }

    missing = required - set(df.columns)

    if missing:
        raise KeyError(
            f"Missing columns: {sorted(missing)}"
        )

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce",
    )

    data = data.dropna(
        subset=[date_column, "sentiment_score"]
    )

    data["period"] = (
        data[date_column]
        .dt.to_period(frequency)
        .dt.to_timestamp()
    )

    data["is_positive"] = (
        data["sentiment_label"] == "positive"
    ).astype(int)

    data["is_negative"] = (
        data["sentiment_label"] == "negative"
    ).astype(int)

    result = (
        data.groupby(
            ["period", brand_column],
            as_index=False,
        )
        .agg(
            mean_sentiment=(
                "sentiment_score", "mean"
            ),
            sentiment_std=(
                "sentiment_score", "std"
            ),
            post_count=(
                "sentiment_score", "size"
            ),
            positive_share=(
                "is_positive", "mean"
            ),
            negative_share=(
                "is_negative", "mean"
            ),
        )
    )

    result["sentiment_std"] = (
        result["sentiment_std"].fillna(0.0)
    )

    return result


def sentiment_summary(
    df: pd.DataFrame,
) -> dict:
    """
    Summarize sentiment analysis results.
    """

    required = {
        "sentiment_score",
        "sentiment_label",
    }

    if not required.issubset(df.columns):
        raise KeyError(
            "Sentiment columns are missing"
        )

    scores = df["sentiment_score"].dropna()
    labels = df["sentiment_label"].value_counts()

    return {
        "total_posts": len(df),
        "average_sentiment": (
            float(scores.mean())
            if len(scores)
            else 0.0
        ),
        "positive_posts": int(
            labels.get("positive", 0)
        ),
        "negative_posts": int(
            labels.get("negative", 0)
        ),
        "neutral_posts": int(
            labels.get("neutral", 0)
        ),
    }

