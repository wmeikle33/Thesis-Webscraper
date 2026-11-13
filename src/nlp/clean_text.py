
"""
Text cleaning utilities for Thesis-Webscraper.

Clean Chinese automotive forum posts before NLP.

Operations:
- Remove HTML markup
- Decode HTML entities
- Remove URLs and email addresses
- Normalize Unicode
- Remove control characters
- Normalize whitespace
- Optionally remove punctuation

This module does not perform tokenization,
stopword removal, or sentiment analysis.
"""

import re
import unicodedata
from html import unescape

import pandas as pd
from bs4 import BeautifulSoup


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+",
    flags=re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

CONTROL_PATTERN = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"
)

WHITESPACE_PATTERN = re.compile(r"\s+")


def remove_html(text: str) -> str:
    """
    Remove HTML tags and preserve readable text.

    Script and style content is discarded.
    """

    soup = BeautifulSoup(text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def remove_urls(text: str) -> str:
    """
    Remove HTTP, HTTPS, and www URLs.
    """

    return URL_PATTERN.sub(" ", text)


def remove_emails(text: str) -> str:
    """
    Remove email addresses from text.
    """

    return EMAIL_PATTERN.sub(" ", text)


def remove_control_characters(text: str) -> str:
    """
    Remove invisible ASCII control characters.
    """

    return CONTROL_PATTERN.sub("", text)


def normalize_unicode(
    text: str,
    form: str = "NFC",
) -> str:
    """
    Normalize Unicode representation.

    NFC preserves most original character forms.
    NFKC also folds compatibility characters,
    including full-width Latin letters and digits.
    """

    if form not in {"NFC", "NFKC"}:
        raise ValueError(
            "Unicode form must be NFC or NFKC"
        )

    return unicodedata.normalize(form, text)


def normalize_whitespace(text: str) -> str:
    """
    Replace repeated whitespace with one space.
    """

    return WHITESPACE_PATTERN.sub(" ", text).strip()


def remove_punctuation(text: str) -> str:
    """
    Remove Unicode punctuation characters.

    Preserves letters, numbers, and symbols.
    """

    return "".join(
        " " if unicodedata.category(char).startswith("P")
        else char
        for char in text
    )


def clean_text(
    text: str | None,
    *,
    strip_html: bool = True,
    strip_urls: bool = True,
    strip_emails: bool = True,
    strip_punctuation: bool = False,
    unicode_form: str = "NFC",
    lowercase_latin: bool = False,
) -> str:
    """
    Clean one forum post.

    Missing values return an empty string.
    """

    if text is None or (
        not isinstance(text, (str, bytes))
        and pd.isna(text)
    ):
        return ""

    if not isinstance(text, str):
        raise TypeError("Text must be a string or missing")

    # Decode HTML entities.
    result = unescape(text)

    # Remove markup.
    if strip_html:
        result = remove_html(result)

    # Normalize Unicode.
    result = normalize_unicode(
        result,
        form=unicode_form,
    )

    # Remove links.
    if strip_urls:
        result = remove_urls(result)

    # Remove email addresses.
    if strip_emails:
        result = remove_emails(result)

    # Remove control characters.
    result = remove_control_characters(result)

    # Optional punctuation removal.
    if strip_punctuation:
        result = remove_punctuation(result)

    # Optional lowercase conversion.
    if lowercase_latin:
        result = result.lower()

    # Normalize whitespace last.
    result = normalize_whitespace(result)

    return result


def clean_dataframe(
    df: pd.DataFrame,
    text_column: str = "body",
    output_column: str = "cleaned_text",
    **cleaning_options,
) -> pd.DataFrame:
    """
    Clean a DataFrame text column.

    Original data is preserved.
    """

    if text_column not in df.columns:
        raise KeyError(
            f"Column '{text_column}' not found"
        )

    result = df.copy()

    result[output_column] = (
        result[text_column].apply(
            lambda value: clean_text(
                value,
                **cleaning_options,
            )
        )
    )

    return result


def cleaning_summary(
    df: pd.DataFrame,
    original_column: str = "body",
    cleaned_column: str = "cleaned_text",
) -> dict:
    """
    Summarize changes after text cleaning.
    """

    for column in (original_column, cleaned_column):
        if column not in df.columns:
            raise KeyError(
                f"Column '{column}' not found"
            )

    original = df[original_column].fillna("").astype(str)
    cleaned = df[cleaned_column].fillna("").astype(str)

    original_lengths = original.str.len()
    cleaned_lengths = cleaned.str.len()

    return {
        "total_documents": len(df),
        "empty_before": int(
            original.str.strip().eq("").sum()
        ),
        "empty_after": int(
            cleaned.str.strip().eq("").sum()
        ),
        "modified_documents": int(
            original.ne(cleaned).sum()
        ),
        "average_length_before": float(
            original_lengths.mean()
        ),
        "average_length_after": float(
            cleaned_lengths.mean()
        ),
        "total_characters_removed": int(
            original_lengths.sum()
            - cleaned_lengths.sum()
        ),
    }

