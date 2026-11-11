
"""
Deduplication utilities for Thesis-Webscraper.

Detect and remove duplicate Chinese automotive forum posts
using IDs, URLs, text content, and similarity scores.
"""

import hashlib
import re
from typing import Any

import pandas as pd
from difflib import SequenceMatcher


def remove_duplicates_by_id(
    df: pd.DataFrame,
    id_column: str = "post_id",
    source_column: str = "source",
    keep: str = "first",
) -> pd.DataFrame:
    """
    Remove duplicate posts using source and post ID.

    Missing IDs are retained rather than treated as
    identical records.
    """
    result = df.copy()

    valid = result[id_column].notna() & (
        result[id_column].astype(str).str.strip() != ""
    )

    identified = result.loc[valid].drop_duplicates(
        subset=[source_column, id_column],
        keep=keep,
    )

    unidentified = result.loc[~valid]

    return pd.concat(
        [identified, unidentified]
    ).sort_index()


def remove_duplicates_by_url(
    df: pd.DataFrame,
    url_column: str = "url",
    keep: str = "first",
) -> pd.DataFrame:
    """
    Remove records with duplicate nonempty URLs.
    """
    result = df.copy()

    valid = result[url_column].notna() & (
        result[url_column].astype(str).str.strip() != ""
    )

    identified = result.loc[valid].drop_duplicates(
        subset=[url_column],
        keep=keep,
    )

    unidentified = result.loc[~valid]

    return pd.concat(
        [identified, unidentified]
    ).sort_index()


def normalize_text(text: Any) -> str:
    """
    Normalize whitespace and common punctuation
    for duplicate comparisons.
    """
    if pd.isna(text):
        return ""

    text = str(text).strip().lower()

    # Normalize repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    # Remove selected Chinese and English punctuation.
    text = re.sub(
        r"[，。！？、；：,.!?;:]",
        "",
        text,
    )

    return text


def remove_duplicates_by_text(
    df: pd.DataFrame,
    text_column: str = "body",
    keep: str = "first",
) -> pd.DataFrame:
    """
    Remove posts with identical normalized text.

    Empty or missing text is retained.
    """
    result = df.copy()

    normalized = result[text_column].map(normalize_text)

    valid = normalized != ""

    identified = result.loc[valid].copy()

    identified["_normalized_text"] = normalized.loc[valid]

    identified = identified.drop_duplicates(
        subset=["_normalized_text"],
        keep=keep,
    ).drop(columns=["_normalized_text"])

    unidentified = result.loc[~valid]

    return pd.concat(
        [identified, unidentified]
    ).sort_index()


def generate_text_hash(text: str) -> str:
    """
    Generate a SHA-256 fingerprint of normalized text.
    """
    normalized = normalize_text(text)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def add_text_hash(
    df: pd.DataFrame,
    text_column: str = "body",
    hash_column: str = "text_hash",
) -> pd.DataFrame:
    """
    Add a text fingerprint column.
    """
    result = df.copy()

    result[hash_column] = result[text_column].map(
        lambda text: (
            generate_text_hash(text)
            if normalize_text(text)
            else pd.NA
        )
    )

    return result


def calculate_similarity(
    text1: str,
    text2: str,
) -> float:
    """
    Calculate similarity between two text strings.

    Returns a score between 0 and 1.
    """
    normalized1 = normalize_text(text1)
    normalized2 = normalize_text(text2)

    if not normalized1 or not normalized2:
        return 0.0

    return SequenceMatcher(
        None,
        normalized1,
        normalized2,
        autojunk=False,
    ).ratio()


def remove_near_duplicates(
    df: pd.DataFrame,
    text_column: str = "body",
    threshold: float = 0.90,
) -> pd.DataFrame:
    """
    Remove near-duplicate posts based on text similarity.

    Intended for relatively small datasets because
    pairwise comparison has quadratic complexity.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must be between 0 and 1"
        )

    result = df.copy()

    texts = result[text_column].map(normalize_text).tolist()

    keep_positions = []

    for i, text in enumerate(texts):

        if not text:
            keep_positions.append(i)
            continue

        is_duplicate = False

        for j in keep_positions:

            if not texts[j]:
                continue

            similarity = calculate_similarity(
                text,
                texts[j],
            )

            if similarity >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            keep_positions.append(i)

    return result.iloc[keep_positions].copy()


def deduplication_summary(
    original_df: pd.DataFrame,
    deduplicated_df: pd.DataFrame,
) -> dict[str, int | float]:
    """
    Calculate basic deduplication statistics.
    """
    original_count = len(original_df)
    final_count = len(deduplicated_df)

    removed = original_count - final_count

    removal_rate = (
        removed / original_count
        if original_count > 0
        else 0.0
    )

    return {
        "original_records": original_count,
        "remaining_records": final_count,
        "removed_records": removed,
        "removal_rate": removal_rate,
    }

