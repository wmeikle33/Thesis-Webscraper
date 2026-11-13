
"""
Principal Component Analysis utilities for Thesis-Webscraper.

Perform dimensionality reduction on numerical features
extracted from Chinese automotive forum discussions.

Feature standardization is handled separately.
"""

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted


def _validate_features(
    X: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate numerical features before PCA.
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
        raise TypeError("All features must be numeric")

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError(
            "Feature matrix contains NaN or infinity"
        )

    return X


def fit_pca(
    X: pd.DataFrame,
    n_components: int | float | None = 0.95,
    random_state: int = 42,
) -> PCA:
    """
    Fit a PCA model to numerical features.

    n_components:
        int   -> fixed number of components
        float -> cumulative explained variance target
                 between 0 and 1
        None  -> retain all available components

    For float thresholds, use the full SVD solver.
    """

    X = _validate_features(X)

    if isinstance(n_components, float):
        if not 0 < n_components < 1:
            raise ValueError(
                "Float n_components must be between 0 and 1"
            )

    elif isinstance(n_components, int):
        if not 1 <= n_components <= min(X.shape):
            raise ValueError(
                "Invalid number of components"
            )

    elif n_components is not None:
        raise TypeError(
            "n_components must be int, float, or None"
        )

    pca = PCA(
        n_components=n_components,
        svd_solver="full",
        random_state=random_state,
    )

    pca.fit(X)

    return pca


def transform_pca(
    pca: PCA,
    X: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform features into principal components.
    """

    check_is_fitted(pca)

    X = _validate_features(X)

    if hasattr(pca, "feature_names_in_"):
        expected = list(pca.feature_names_in_)

        if list(X.columns) != expected:
            raise ValueError(
                "Feature columns must match training order"
            )

    transformed = pca.transform(X)

    columns = [
        f"PC{i + 1}"
        for i in range(transformed.shape[1])
    ]

    return pd.DataFrame(
        transformed,
        index=X.index,
        columns=columns,
    )


def fit_transform_pca(
    X: pd.DataFrame,
    n_components: int | float | None = 0.95,
) -> tuple[pd.DataFrame, PCA]:
    """
    Fit PCA and return transformed data
    together with the fitted model.
    """

    pca = fit_pca(
        X,
        n_components=n_components,
    )

    transformed = transform_pca(pca, X)

    return transformed, pca


def explained_variance(
    pca: PCA,
) -> pd.DataFrame:
    """
    Return explained variance for each component.
    """

    check_is_fitted(pca)

    ratios = pca.explained_variance_ratio_

    return pd.DataFrame({
        "component": [
            f"PC{i + 1}"
            for i in range(len(ratios))
        ],
        "explained_variance_ratio": ratios,
        "cumulative_explained_variance": (
            np.cumsum(ratios)
        ),
        "eigenvalue": pca.explained_variance_,
    })


def get_component_weights(
    pca: PCA,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Return PCA component coefficients.

    Rows are original features.
    Columns are principal components.
    """

    check_is_fitted(pca)

    if len(feature_names) != pca.n_features_in_:
        raise ValueError(
            "Feature count does not match PCA model"
        )

    return pd.DataFrame(
        pca.components_.T,
        index=feature_names,
        columns=[
            f"PC{i + 1}"
            for i in range(pca.n_components_)
        ],
    )


def reconstruct_features(
    pca: PCA,
    X_pca: pd.DataFrame,
) -> pd.DataFrame:
    """
    Reconstruct features from principal components.

    Reconstruction may be approximate when
    dimensionality has been reduced.
    """

    check_is_fitted(pca)

    reconstructed = pca.inverse_transform(
        X_pca.to_numpy()
    )

    feature_names = (
        list(pca.feature_names_in_)
        if hasattr(pca, "feature_names_in_")
        else [
            f"feature_{i}"
            for i in range(pca.n_features_in_)
        ]
    )

    return pd.DataFrame(
        reconstructed,
        index=X_pca.index,
        columns=feature_names,
    )


def reconstruction_error(
    X_original: pd.DataFrame,
    X_reconstructed: pd.DataFrame,
) -> float:
    """
    Calculate mean squared reconstruction error.
    """

    if X_original.shape != X_reconstructed.shape:
        raise ValueError(
            "Original and reconstructed shapes differ"
        )

    if list(X_original.columns) != list(
        X_reconstructed.columns
    ):
        raise ValueError(
            "Feature columns do not match"
        )

    error = np.mean(
        (
            X_original.to_numpy(dtype=float)
            - X_reconstructed.to_numpy(dtype=float)
        ) ** 2
    )

    return float(error)


def save_pca(
    pca: PCA,
    file_path: str | Path,
) -> None:
    """
    Save a fitted PCA model.
    """

    check_is_fitted(pca)

    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(pca, path)


def load_pca(
    file_path: str | Path,
) -> PCA:
    """
    Load a previously saved PCA model.

    Only load trusted files because joblib
    uses pickle-based serialization.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(path)

    pca = joblib.load(path)

    if not isinstance(pca, PCA):
        raise TypeError(
            "Loaded object is not a PCA model"
        )

    check_is_fitted(pca)

    return pca

