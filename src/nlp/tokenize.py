
"""
Chinese tokenization utilities for Thesis-Webscraper.

Features:
- Chinese word segmentation with Jieba
- Custom automotive dictionaries
- Sentence segmentation
- Part-of-speech tagging
- DataFrame tokenization
- Token frequency analysis
- Tokenization statistics

Stopword removal is handled separately
in src/nlp/stopwords.py.
"""

from collections import Counter
from collections.abc import Iterable
from pathlib import Path
import re

import jieba
import jieba.posseg as pseg
import pandas as pd


AUTOMOTIVE_TERMS = {
    "比亚迪",
    "特斯拉",
    "蔚来",
    "小鹏汽车",
    "理想汽车",
    "刀片电池",
    "固态电池",
    "动力电池",
    "电池寿命",
    "续航里程",
    "里程焦虑",
    "快速充电",
    "充电桩",
    "充电速度",
    "自动驾驶",
    "智能驾驶",
    "辅助驾驶",
    "新能源汽车",
    "电动汽车",
    "性价比",
}


SENTENCE_PATTERN = re.compile(
    r"(?<=[。！？!?；;])\s*"
)


class ChineseTokenizer:
    """
    Reusable Chinese tokenizer with a
    customizable automotive vocabulary.
    """

    def __init__(
        self,
        custom_words: Iterable[str] | None = None,
        dictionary_path: str | Path | None = None,
        include_automotive_terms: bool = True,
    ):
        self.tokenizer = jieba.Tokenizer()

        if include_automotive_terms:
            self.add_custom_words(AUTOMOTIVE_TERMS)

        if custom_words is not None:
            self.add_custom_words(custom_words)

        if dictionary_path is not None:
            self.load_custom_dictionary(dictionary_path)

    def add_custom_words(
        self,
        words: Iterable[str],
    ) -> None:
        """
        Register custom vocabulary terms.
        """

        for word in words:
            word = word.strip()

            if word:
                self.tokenizer.add_word(
                    word,
                    freq=1000000,
                )

    def load_custom_dictionary(
        self,
        file_path: str | Path,
    ) -> None:
        """
        Load a Jieba-format user dictionary.

        Each line can contain:
            word
            word frequency
            word frequency POS
        """

        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(path)

        self.tokenizer.load_userdict(str(path))

    def tokenize_chinese(
        self,
        text: str,
        mode: str = "accurate",
        keep_punctuation: bool = False,
    ) -> list[str]:
        """
        Tokenize Chinese text.

        mode:
            accurate -> standard Jieba segmentation
            full     -> all possible word matches
            search   -> search-engine segmentation
        """

        if not isinstance(text, str) or not text.strip():
            return []

        if mode == "accurate":
            tokens = self.tokenizer.lcut(
                text,
                cut_all=False,
            )

        elif mode == "full":
            tokens = self.tokenizer.lcut(
                text,
                cut_all=True,
            )

        elif mode == "search":
            tokens = list(
                self.tokenizer.cut_for_search(text)
            )

        else:
            raise ValueError(
                "mode must be accurate, full, or search"
            )

        tokens = [
            token.strip()
            for token in tokens
            if token.strip()
        ]

        if not keep_punctuation:
            tokens = [
                token
                for token in tokens
                if any(
                    char.isalnum()
                    for char in token
                )
            ]

        return tokens

    def tokenize_with_pos(
        self,
        text: str,
    ) -> list[tuple[str, str]]:
        """
        Return (token, POS tag) pairs.

        Uses Jieba's POS tokenizer with the
        same underlying custom dictionary.
        """

        if not isinstance(text, str) or not text.strip():
            return []

        pos_tokenizer = pseg.POSTokenizer(
            self.tokenizer
        )

        return [
            (item.word, item.flag)
            for item in pos_tokenizer.cut(text)
            if item.word.strip()
        ]


def tokenize_chinese(
    text: str,
    mode: str = "accurate",
    keep_punctuation: bool = False,
    tokenizer: ChineseTokenizer | None = None,
) -> list[str]:
    """
    Convenience wrapper for tokenization.
    """

    if tokenizer is None:
        tokenizer = DEFAULT_TOKENIZER

    return tokenizer.tokenize_chinese(
        text,
        mode=mode,
        keep_punctuation=keep_punctuation,
    )


def tokenize_sentences(
    text: str,
) -> list[str]:
    """
    Split Chinese text into sentences.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    return [
        sentence.strip()
        for sentence in SENTENCE_PATTERN.split(text)
        if sentence.strip()
    ]


def tokenize_dataframe(
    df: pd.DataFrame,
    text_column: str = "normalized_text",
    output_column: str = "tokens",
    tokenizer: ChineseTokenizer | None = None,
    mode: str = "accurate",
) -> pd.DataFrame:
    """
    Tokenize a DataFrame text column.

    Preserves all original columns.
    """

    if text_column not in df.columns:
        raise KeyError(
            f"Missing column: {text_column}"
        )

    if tokenizer is None:
        tokenizer = DEFAULT_TOKENIZER

    result = df.copy()

    result[output_column] = (
        result[text_column].apply(
            lambda text: tokenizer.tokenize_chinese(
                text,
                mode=mode,
            )
        )
    )

    return result


def get_token_frequencies(
    tokenized_documents: Iterable[Iterable[str]],
    top_n: int | None = 20,
) -> pd.DataFrame:
    """
    Count token occurrences across documents.
    """

    counter = Counter()

    for tokens in tokenized_documents:
        counter.update(tokens)

    counts = counter.most_common(top_n)

    return pd.DataFrame(
        counts,
        columns=["token", "frequency"],
    )


def tokenization_summary(
    tokenized_documents: Iterable[Iterable[str]],
) -> dict:
    """
    Summarize tokenized document statistics.
    """

    documents = [
        list(tokens)
        for tokens in tokenized_documents
    ]

    token_counts = [
        len(tokens)
        for tokens in documents
    ]

    unique_tokens = {
        token
        for tokens in documents
        for token in tokens
    }

    return {
        "total_documents": len(documents),
        "total_tokens": sum(token_counts),
        "unique_tokens": len(unique_tokens),
        "average_tokens_per_document": (
            sum(token_counts) / len(documents)
            if documents
            else 0.0
        ),
        "empty_documents": sum(
            count == 0
            for count in token_counts
        ),
    }


# Shared default tokenizer.
DEFAULT_TOKENIZER = ChineseTokenizer()

