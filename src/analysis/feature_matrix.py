
"""
Feature engineering for Thesis-Webscraper.

Convert Chinese automotive forum discussions into
numerical features for PCA and regression.
"""

from collections.abc import Sequence

import jieba
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


EV_KEYWORDS = {
    "battery": ["电池", "电量", "电池寿命"],
    "range": ["续航", "里程", "续航里程"],
    "charging": ["充电", "充电桩", "快充"],
    "price": ["价格", "售价", "性价比"],
    "safety": ["安全", "碰撞", "刹车"],
    "performance": ["加速", "动力", "性能"],
    "brand": ["品牌", "特斯拉", "比亚迪"],
}


def tokenize_chinese(
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


def build_keyword_features(
    df: pd.DataFrame,
    text_column: str = "body",
    keyword_categories: dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """
    Count occurrences of EV-related keywords
    for each forum post.

    Returns one numerical row per post.
    """

    if keyword_categories is None:
        keyword_categories = EV_KEYWORDS

    if text_column not in df.columns:
        raise KeyError(
            f"Missing text column: {text_column}"
        )

    result = pd.DataFrame(index=df.index)

    texts = df[text_column].fillna("").astype(str)

    for category, keywords in keyword_categories.items():

        result[f"keyword_{category}"] = texts.map(
            lambda text: sum(
                text.count(keyword)
                for keyword in keywords
            )
        )

    return result


def build_tfidf_features(
    texts: Sequence[str],
    max_features: int = 500,
    min_df: int = 1,
    max_df: float = 1.0,
) -> tuple[pd.DataFrame, TfidfVectorizer]:
    """
    Convert Chinese text into TF-IDF features.

    Returns the feature matrix and fitted vectorizer.
    """

    vectorizer = TfidfVectorizer(
        tokenizer=tokenize_chinese,
        token_pattern=None,
        lowercase=False,
        max_features=max_features,
        min_df=min_df,
        max_df=max_df,
    )

    cleaned_texts = [
        text if isinstance(text, str) else ""
        for text in texts
    ]

    matrix = vectorizer.fit_transform(cleaned_texts)

    feature_names = [
        f"tfidf_{term}"
        for term in vectorizer.get_feature_names_out()
    ]

    features = pd.DataFrame(
        matrix.toarray(),
        columns=feature_names,
    )

    return features, vectorizer


def add_text_length_features(
    df: pd.DataFrame,
    text_column: str = "body",
) -> pd.DataFrame:
    """
    Calculate basic text-length statistics.
    """

    texts = df[text_column].fillna("").astype(str)

    return pd.DataFrame({
        "character_count": texts.str.len(),
        "token_count": texts.map(
            lambda text: len(tokenize_chinese(text))
        ),
    }, index=df.index)


def add_sentiment_features(
    df: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
) -> pd.DataFrame:
    """
    Extract sentiment scores calculated by an
    upstream sentiment analysis module.
    """

    if sentiment_column not in df.columns:
        raise KeyError(
            f"Missing sentiment column: {sentiment_column}"
        )

    return pd.DataFrame({
        "sentiment_score": pd.to_numeric(
            df[sentiment_column],
            errors="coerce",
        )
    }, index=df.index)


def build_post_feature_matrix(
    df: pd.DataFrame,
    include_tfidf: bool = False,
    include_sentiment: bool = False,
    max_tfidf_features: int = 500,
) -> pd.DataFrame:
    """
    Combine multiple feature extraction methods.

    Each row represents one forum post.
    """

    features = [
        build_keyword_features(df),
        add_text_length_features(df),
    ]

    if include_sentiment:
        features.append(
            add_sentiment_features(df)
        )

    if include_tfidf:
        tfidf_features, _ = build_tfidf_features(
            df["body"].fillna("").astype(str).tolist(),
            max_features=max_tfidf_features,
        )

        tfidf_features.index = df.index

        features.append(tfidf_features)

    return pd.concat(features, axis=1)


def aggregate_features(
    features: pd.DataFrame,
    metadata: pd.DataFrame,
    date_column: str = "created_at",
    brand_column: str = "brand",
    frequency: str = "D",
) -> pd.DataFrame:
    """
    Aggregate post-level features by brand and date.

    Numerical features are averaged within each group.
    """

    if len(features) != len(metadata):
        raise ValueError(
            "Features and metadata must have equal lengths"
        )

    data = features.reset_index(drop=True).copy()
    meta = metadata.reset_index(drop=True)

    data[date_column] = pd.to_datetime(
        meta[date_column],
        errors="coerce",
    )

    data[brand_column] = meta[brand_column]

    data = data.dropna(
        subset=[date_column, brand_column]
    )

    data[date_column] = data[date_column].dt.to_period(
        frequency
    ).dt.to_timestamp()

    numeric_columns = features.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    aggregated = (
        data.groupby(
            [brand_column, date_column],
            as_index=False,
        )[numeric_columns]
        .mean()
    )

    counts = (
        data.groupby(
            [brand_column, date_column]
        )
        .size()
        .rename("post_count")
        .reset_index()
    )

    return aggregated.merge(
        counts,
        on=[brand_column, date_column],
        how="left",
        validate="one_to_one",
    )


def merge_financial_data(
    features: pd.DataFrame,
    financial_data: pd.DataFrame,
    date_column: str = "created_at",
    brand_column: str = "brand",
) -> pd.DataFrame:
    """
    Merge text-derived features with financial data.

    Requires pre-aligned observation dates and
    a consistent brand/company identifier.
    """

    financial = financial_data.copy()

    financial[date_column] = pd.to_datetime(
        financial[date_column]
    )

    text_features = features.copy()

    text_features[date_column] = pd.to_datetime(
        text_features[date_column]
    )

    return text_features.merge(
        financial,
        on=[brand_column, date_column],
        how="inner",
        validate="one_to_one",
    )


def select_numeric_features(
    df: pd.DataFrame,
    exclude_columns: Sequence[str] = (
        "stock_return",
        "post_count",
    ),
) -> pd.DataFrame:
    """
    Select numerical predictor columns for PCA.

    Excludes the target variable and selected
    metadata/count columns.
    """

    numeric = df.select_dtypes(
        include=[np.number]
    )

    return numeric.drop(
        columns=list(exclude_columns),
        errors="ignore",
    )

