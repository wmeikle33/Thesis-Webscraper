
"""
Data ingestion module for Thesis-Webscraper.

Loads scraped automotive forum data from multiple sources
and standardizes it into pandas DataFrames.
"""

import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


REQUIRED_COLUMNS = [
    "post_id",
    "source",
    "title",
    "body",
    "created_at",
    "scraped_at",
    "brand",
    "model",
    "url",
]

COLUMN_ALIASES = {
    "id": "post_id",
    "content": "body",
    "text": "body",
    "date": "created_at",
    "timestamp": "created_at",
    "manufacturer": "brand",
    "vehicle_model": "model",
    "link": "url",
}


def normalize_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize column names and add missing fields.
    """

    df = df.copy()

    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    df = df.rename(columns=COLUMN_ALIASES)

    if not df.columns.is_unique:
        raise ValueError(
            "Duplicate columns after normalization"
        )

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    return df


def ingest_records(
    records: Iterable[dict[str, Any]],
) -> pd.DataFrame:
    """
    Ingest scraped records from parser.py.
    """

    df = pd.DataFrame.from_records(records)

    return normalize_columns(df)


def ingest_csv(
    file_path: str | Path,
    encoding: str = "utf-8-sig",
) -> pd.DataFrame:
    """
    Load CSV data while preserving string identifiers.
    """

    df = pd.read_csv(
        file_path,
        encoding=encoding,
        dtype=str,
    )

    return normalize_columns(df)


def ingest_json(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Load a JSON array containing scraped records.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "JSON must contain a list of records"
        )

    return ingest_records(records)


def ingest_jsonl(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Load newline-delimited JSON records.
    """

    records = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(file, 1):

            if not line.strip():
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(
                    f"Expected an object on line {line_number}"
                )

            records.append(record)

    return ingest_records(records)


def ingest_parquet(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Load a Parquet dataset.
    """

    df = pd.read_parquet(file_path)

    return normalize_columns(df)


def ingest_file(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Select the ingestion function based on file type.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return ingest_csv(path)

    elif suffix == ".json":
        return ingest_json(path)

    elif suffix == ".jsonl":
        return ingest_jsonl(path)

    elif suffix == ".parquet":
        return ingest_parquet(path)

    else:
        raise ValueError(
            f"Unsupported file format: {suffix}"
        )


def ingest_directory(
    directory: str | Path,
) -> pd.DataFrame:
    """
    Load and combine supported files from a directory.
    """

    path = Path(directory)

    if not path.is_dir():
        raise NotADirectoryError(path)

    supported_formats = {
        ".csv",
        ".json",
        ".jsonl",
        ".parquet",
    }

    files = sorted(
        file
        for file in path.iterdir()
        if file.is_file()
        and file.suffix.lower() in supported_formats
    )

    if not files:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    frames = [
        ingest_file(file)
        for file in files
    ]

    return pd.concat(
        frames,
        ignore_index=True,
    )


def ingestion_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return information about an ingested dataset.
    """

    return {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "missing_values": df.isna().sum().to_dict(),
        "sources": (
            df["source"].dropna().unique().tolist()
            if "source" in df.columns
            else []
        ),
    }

