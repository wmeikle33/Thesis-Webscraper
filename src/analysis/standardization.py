
"""
Feature standardization utilities for Thesis-Webscraper.

Prepare numerical predictors for PCA and regression.

Supported methods:
- Z-score standardization
- Min-Max scaling
- Robust scaling
- Inverse transformation
- Scaler persistence
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
)


Scaler = StandardScaler | MinMaxScaler | RobustScaler


def validate_features(
    X: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate the feature matrix before scaling.
    """

    if not isinstance(X, pd.DataFrame):
        raise TypeError("X must be a pandas DataFrame")

    if X.empty:
        raise ValueError("Feature matrix cannot be empty")

    if not X.columns.is_unique:
        raise ValueError("Feature names must be unique")

    if not all(
        pd.api.types.is_numeric_dtype(dtype)
        for dtype in X.dtypes
    ):
        raise TypeError("All columns must be numeric")

    if not np.isfinite(
        X.to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Features contain NaN or infinity"
        )

    return X


def fit_standard_scaler(
    X: pd.DataFrame,
) -> StandardScaler:
    """
    Fit a StandardScaler to training features.

    Learns the mean and standard deviation
    of each column.
    """

    X = validate_features(X)

    scaler = StandardScaler()
    scaler.fit(X)

    return scaler


def transform_features(
    X: pd.DataFrame,
    scaler: Scaler,
) -> pd.DataFrame:
    """
    Apply a previously fitted scaler.

    Preserves DataFrame columns and index.
    """

    X = validate_features(X)

    if hasattr(scaler, "feature_names_in_"):
        expected = list(scaler.feature_names_in_)

        if list(X.columns) != expected:
            raise ValueError(
                "Feature columns must match training order"
            )

    transformed = scaler.transform(X)

    return pd.DataFrame(
        transformed,
        columns=X.columns,
        index=X.index,
    )


def fit_transform_standard(
    X: pd.DataFrame,
) -> tuple[pd.DataFrame, StandardScaler]:
    """
    Fit a StandardScaler and transform features.

    Returns both the transformed DataFrame
    and fitted scaler.
    """

    scaler = fit_standard_scaler(X)

    transformed = transform_features(
        X,
        scaler,
    )

    return transformed, scaler


def minmax_scale(
    X: pd.DataFrame,
    feature_range: tuple[float, float] = (0, 1),
) -> tuple[pd.DataFrame, MinMaxScaler]:
    """
    Scale features to a specified range.
    """

    X = validate_features(X)

    scaler = MinMaxScaler(
        feature_range=feature_range
    )

    scaler.fit(X)

    transformed = transform_features(
        X,
        scaler,
    )

    return transformed, scaler


def robust_scale(
    X: pd.DataFrame,
) -> tuple[pd.DataFrame, RobustScaler]:
    """
    Scale features using median and IQR.

    Useful when features contain outliers.
    """

    X = validate_features(X)

    scaler = RobustScaler()

    scaler.fit(X)

    transformed = transform_features(
        X,
        scaler,
    )

    return transformed, scaler


def inverse_standardize(
    X_scaled: pd.DataFrame,
    scaler: Scaler,
) -> pd.DataFrame:
    """
    Restore scaled features to original units.
    """

    restored = scaler.inverse_transform(
        X_scaled
    )

    return pd.DataFrame(
        restored,
        columns=X_scaled.columns,
        index=X_scaled.index,
    )


def get_scaling_statistics(
    scaler: StandardScaler,
) -> pd.DataFrame:
    """
    Return learned feature means and scales.
    """

    from sklearn.utils.validation import check_is_fitted

    check_is_fitted(scaler)

    feature_names = (
        list(scaler.feature_names_in_)
        if hasattr(scaler, "feature_names_in_")
        else [
            f"feature_{i}"
            for i in range(scaler.n_features_in_)
        ]
    )

    return pd.DataFrame({
        "feature": feature_names,
        "mean": scaler.mean_,
        "scale": scaler.scale_,
        "variance": scaler.var_,
    })


def save_scaler(
    scaler: Scaler,
    file_path: str | Path,
) -> None:
    """
    Save a fitted scaler to disk.
    """

    from sklearn.utils.validation import check_is_fitted

    check_is_fitted(scaler)

    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(scaler, path)


def load_scaler(
    file_path: str | Path,
) -> Scaler:
    """
    Load a saved scaler from a trusted file.

    Do not load untrusted joblib files.
    """

    from sklearn.utils.validation import check_is_fitted

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(path)

    scaler = joblib.load(path)

    if not isinstance(
        scaler,
        (StandardScaler, MinMaxScaler, RobustScaler),
    ):
        raise TypeError("Unsupported scaler type")

    check_is_fitted(scaler)

    return scaler

