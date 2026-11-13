
"""
Text normalization for Thesis-Webscraper.

Standardizes Chinese automotive forum text.

Features:
- Unicode normalization
- Traditional/Simplified Chinese conversion
- Brand-name normalization
- EV terminology normalization
- Whitespace normalization
- DataFrame processing

Original text should be retained separately.
"""

import re
import unicodedata
from collections.abc import Mapping

import pandas as pd


# Conservative brand aliases.
# Avoid generic terms such as "理想" or "小鹏"
# unless context disambiguation is available.

BRAND_ALIASES = {
    "BYD": [
        "比亚迪",
        "ＢＹＤ",
        "BYD",
    ],
    "Tesla": [
        "特斯拉",
        "TESLA",
        "Tesla",
    ],
    "NIO": [
        "蔚来汽车",
        "蔚来",
        "NIO",
    ],
    "XPENG": [
        "小鹏汽车",
        "XPENG",
    ],
    "Li Auto": [
        "理想汽车",
        "Li Auto",
    ],
}


# Terms should only be merged when the
# equivalence is appropriate for the research.

EV_TERM_ALIASES = {
    "新能源汽车": [
        "新能源车",
        "新能源汽车",
    ],
    "电动汽车": [
        "纯电动汽车",
        "纯电动车",
        "电动汽车",
    ],
    "快速充电": [
        "快充",
        "快速充电",
    ],
}


def normalize_unicode(
    text: str,
    form: str = "NFKC",
) -> str:
    """
    Normalize Unicode character representations.

    NFKC converts many full-width Latin letters,
    numbers, and compatibility characters.
    """

    if form not in {"NFC", "NFKC"}:
        raise ValueError(
            "form must be 'NFC' or 'NFKC'"
        )

    return unicodedata.normalize(form, text)


def convert_chinese_script(
    text: str,
    configuration: str = "t2s",
) -> str:
    """
    Convert Traditional Chinese to Simplified
    Chinese using OpenCC.

    configuration:
        t2s -> Traditional to Simplified
        s2t -> Simplified to Traditional
    """

    try:
        from opencc import OpenCC
    except ImportError as exc:
        raise ImportError(
            "Install OpenCC with: pip install opencc-python-reimplemented"
        ) from exc

    converter = OpenCC(configuration)

    return converter.convert(text)


def replace_aliases(
    text: str,
    aliases: Mapping[str, list[str]],
    *,
    ignore_case: bool = False,
) -> str:
    """
    Replace aliases with their canonical terms.

    Longer aliases are matched first to reduce
    partial matching conflicts.

    ASCII aliases use word boundaries so that
    a term such as NIO does not match inside
    a longer English identifier.
    """

    replacements = []

    for canonical, variants in aliases.items():
        for variant in variants:
            if variant:
                replacements.append(
                    (variant, canonical)
                )

    replacements.sort(
        key=lambda item: len(item[0]),
        reverse=True,
    )

    if not replacements:
        return text

    lookup = {}
    patterns = []

    flags = re.IGNORECASE if ignore_case else 0

    for index, (variant, canonical) in enumerate(
        replacements
    ):
        # ASCII names should not match inside
        # longer alphanumeric identifiers.
        escaped = re.escape(variant)

        if variant.isascii() and variant.isalnum():
            escaped = (
                rf"(?<![A-Za-z0-9])"
                rf"{escaped}"
                rf"(?![A-Za-z0-9])"
            )

        patterns.append(
            f"(?P<alias_{index}>{escaped})"
        )

        lookup[f"alias_{index}"] = canonical

    pattern = re.compile(
        "|".join(patterns),
        flags=flags,
    )

    return pattern.sub(
        lambda match: lookup[match.lastgroup],
        text,
    )


def normalize_brand_names(
    text: str,
    aliases: Mapping[
        str, list[str]
    ] | None = None,
) -> str:
    """
    Normalize supported automotive brand names.
    """

    if aliases is None:
        aliases = BRAND_ALIASES

    return replace_aliases(
        text,
        aliases,
        ignore_case=True,
    )


def normalize_ev_terms(
    text: str,
    aliases: Mapping[
        str, list[str]
    ] | None = None,
) -> str:
    """
    Normalize selected EV terminology.
    """

    if aliases is None:
        aliases = EV_TERM_ALIASES

    return replace_aliases(
        text,
        aliases,
    )


def normalize_whitespace(text: str) -> str:
    """
    Collapse repeated whitespace.
    """

    return re.sub(r"\s+", " ", text).strip()


def normalize_text(
    text: str | None,
    *,
    unicode_form: str = "NFKC",
    convert_script: bool = False,
    normalize_brands: bool = True,
    normalize_terms: bool = True,
    brand_aliases: Mapping[
        str, list[str]
    ] | None = None,
    term_aliases: Mapping[
        str, list[str]
    ] | None = None,
) -> str:
    """
    Apply configurable normalization steps.
    """

    if text is None or (
        not isinstance(text, str)
        and pd.isna(text)
    ):
        return ""

    if not isinstance(text, str):
        raise TypeError(
            "Text must be a string or missing"
        )

    result = normalize_unicode(
        text,
        form=unicode_form,
    )

    if convert_script:
        result = convert_chinese_script(
            result,
            configuration="t2s",
        )

    if normalize_brands:
        result = normalize_brand_names(
            result,
            aliases=brand_aliases,
        )

    if normalize_terms:
        result = normalize_ev_terms(
            result,
            aliases=term_aliases,
        )

    return normalize_whitespace(result)


def normalize_dataframe(
    df: pd.DataFrame,
    text_column: str = "cleaned_text",
    output_column: str = "normalized_text",
    **normalization_options,
) -> pd.DataFrame:
    """
    Normalize a DataFrame text column.

    Preserves the original DataFrame.
    """

    if text_column not in df.columns:
        raise KeyError(
            f"Missing column: {text_column}"
        )

    result = df.copy()

    result[output_column] = (
        result[text_column].apply(
            lambda value: normalize_text(
                value,
                **normalization_options,
            )
        )
    )

    return result


def normalization_summary(
    df: pd.DataFrame,
    original_column: str = "cleaned_text",
    normalized_column: str = "normalized_text",
) -> dict:
    """
    Summarize text normalization changes.
    """

    for column in (
        original_column,
        normalized_column,
    ):
        if column not in df.columns:
            raise KeyError(
                f"Missing column: {column}"
            )

    original = (
        df[original_column]
        .fillna("")
        .astype(str)
    )

    normalized = (
        df[normalized_column]
        .fillna("")
        .astype(str)
    )

    changed = original != normalized

    return {
        "total_documents": len(df),
        "modified_documents": int(
            changed.sum()
        ),
        "unchanged_documents": int(
            (~changed).sum()
        ),
        "modification_rate": (
            float(changed.mean())
            if len(df)
            else 0.0
        ),
    }
