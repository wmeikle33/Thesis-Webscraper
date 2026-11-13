
"""
Regression utilities for Thesis-Webscraper.

Fit regression models relating Chinese automotive
forum features to financial outcomes.

Supported models:
- Ordinary Least Squares (OLS)
- Principal Component Regression (PCR)
- Ridge Regression
- Lasso Regression
- Time-series cross-validation
"""

from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm

from sklearn.base import clone
from sklearn.decomposition import PCA
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def _validate_xy(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Validate predictors and regression target.

    Inputs must already be aligned by observation.
    """

    if not isinstance(X, pd.DataFrame):
        raise TypeError("X must be a DataFrame")

    if not isinstance(y, pd.Series):
        raise TypeError("y must be a Series")

    if X.empty or len(X) != len(y):
        raise ValueError("Invalid X and y dimensions")

    if not X.columns.is_unique:
        raise ValueError("Feature names must be unique")

    if not all(
        pd.api.types.is_numeric_dtype(dtype)
        for dtype in X.dtypes
    ):
        raise TypeError("X must contain numeric features")

    if not np.isfinite(
        X.to_numpy(dtype=float)
    ).all():
        raise ValueError("X contains missing/nonfinite values")

    if not np.isfinite(
        y.to_numpy(dtype=float)
    ).all():
        raise ValueError("y contains missing/nonfinite values")

    return X, y


def fit_ols(
    X: pd.DataFrame,
    y: pd.Series,
    covariance_type: str = "nonrobust",
    maxlags: int = 5,
) -> Any:
    """
    Fit Ordinary Least Squares regression.

    covariance_type:
        nonrobust -> conventional standard errors
        HC3       -> heteroskedasticity-robust errors
        HAC       -> heteroskedasticity/autocorrelation
                     consistent errors
    """

    X, y = _validate_xy(X, y)

    X_const = sm.add_constant(
        X,
        has_constant="add",
    )

    model = sm.OLS(y, X_const)

    if covariance_type == "HAC":
        return model.fit(
            cov_type="HAC",
            cov_kwds={"maxlags": maxlags},
        )

    if covariance_type == "HC3":
        return model.fit(cov_type="HC3")

    if covariance_type == "nonrobust":
        return model.fit()

    raise ValueError("Unsupported covariance type")


def fit_pcr(
    X: pd.DataFrame,
    y: pd.Series,
    n_components: int = 3,
) -> Pipeline:
    """
    Fit Principal Component Regression.

    Standardization, PCA, and regression are
    fitted together in one pipeline.
    """

    X, y = _validate_xy(X, y)

    if not 1 <= n_components <= min(X.shape):
        raise ValueError("Invalid n_components")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=n_components)),
        ("regression", LinearRegression()),
    ])

    pipeline.fit(X, y)

    return pipeline


def fit_ridge(
    X: pd.DataFrame,
    y: pd.Series,
    alpha: float = 1.0,
) -> Pipeline:
    """
    Fit Ridge regression with L2 regularization.
    """

    X, y = _validate_xy(X, y)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regression", Ridge(alpha=alpha)),
    ])

    pipeline.fit(X, y)

    return pipeline


def fit_lasso(
    X: pd.DataFrame,
    y: pd.Series,
    alpha: float = 0.01,
) -> Pipeline:
    """
    Fit Lasso regression with L1 regularization.
    """

    X, y = _validate_xy(X, y)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regression", Lasso(
            alpha=alpha,
            max_iter=10000,
        )),
    ])

    pipeline.fit(X, y)

    return pipeline


def predict_regression(
    model: Any,
    X: pd.DataFrame,
) -> np.ndarray:
    """
    Generate predictions using a fitted model.

    Supports sklearn estimators/pipelines and
    statsmodels regression results.
    """

    if not isinstance(X, pd.DataFrame):
        raise TypeError("X must be a DataFrame")

    if hasattr(model, "model") and hasattr(
        model.model, "exog_names"
    ):
        expected = [
            name for name in model.model.exog_names
            if name != "const"
        ]

        X = X.loc[:, expected]

        X = sm.add_constant(
            X,
            has_constant="add",
        )

        X = X.loc[:, model.model.exog_names]

    predictions = model.predict(X)

    return np.asarray(predictions).ravel()


def evaluate_regression(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, float]:
    """
    Calculate regression evaluation metrics.
    """

    actual = np.asarray(y_true).ravel()
    predicted = np.asarray(y_pred).ravel()

    if actual.shape != predicted.shape:
        raise ValueError("Prediction shape mismatch")

    if len(actual) < 2:
        raise ValueError("At least two observations required")

    mse = mean_squared_error(actual, predicted)

    return {
        "r2": float(r2_score(actual, predicted)),
        "mae": float(
            mean_absolute_error(actual, predicted)
        ),
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
    }


def time_series_cross_validation(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    gap: int = 0,
) -> pd.DataFrame:
    """
    Evaluate a sklearn model using chronological splits.

    X and y must be sorted by observation time.
    Preprocessing should be inside the pipeline.
    """

    X, y = _validate_xy(X, y)

    splitter = TimeSeriesSplit(
        n_splits=n_splits,
        gap=gap,
    )

    results = []

    for fold, (train_idx, test_idx) in enumerate(
        splitter.split(X),
        start=1,
    ):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        fitted = clone(model)

        fitted.fit(X_train, y_train)

        predictions = fitted.predict(X_test)

        metrics = evaluate_regression(
            y_test,
            predictions,
        )

        results.append({
            "fold": fold,
            "train_size": len(train_idx),
            "test_size": len(test_idx),
            **metrics,
        })

    return pd.DataFrame(results)


def compare_models(
    models: dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    """
    Compare sklearn models on the same test set.
    """

    results = []

    for name, model in models.items():
        fitted = clone(model)

        fitted.fit(X_train, y_train)

        predictions = fitted.predict(X_test)

        metrics = evaluate_regression(
            y_test,
            predictions,
        )

        results.append({
            "model": name,
            **metrics,
        })

    return pd.DataFrame(results).sort_values(
        "rmse",
        ascending=True,
    ).reset_index(drop=True)

