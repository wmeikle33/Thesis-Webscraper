
"""
Statistical diagnostics for Thesis-Webscraper.

Evaluate regression performance, residual behavior,
multicollinearity, and PCA explained variance.
"""

from typing import Any

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from statsmodels.stats.diagnostic import (
    het_breuschpagan,
    acorr_ljungbox,
)

from statsmodels.stats.outliers_influence import (
    variance_inflation_factor,
)

from statsmodels.stats.stattools import (
    durbin_watson,
    jarque_bera,
)


def regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, float]:
    """
    Calculate regression performance metrics.
    """

    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()

    if y_true.shape != y_pred.shape:
        raise ValueError(
            "y_true and y_pred must have the same shape"
        )

    if len(y_true) == 0:
        raise ValueError("Input arrays cannot be empty")

    if not (
        np.isfinite(y_true).all()
        and np.isfinite(y_pred).all()
    ):
        raise ValueError("Inputs must contain finite values")

    mse = mean_squared_error(y_true, y_pred)

    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
    }


def calculate_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> np.ndarray:
    """
    Calculate regression residuals.
    """

    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()

    if y_true.shape != y_pred.shape:
        raise ValueError("Input shapes do not match")

    return y_true - y_pred


def residual_summary(
    residuals: np.ndarray,
) -> dict[str, float]:
    """
    Summarize the distribution of residuals.
    """

    residuals = np.asarray(
        residuals,
        dtype=float,
    ).ravel()

    if len(residuals) == 0:
        raise ValueError("Residuals cannot be empty")

    return {
        "mean": float(np.mean(residuals)),
        "std": float(np.std(residuals, ddof=1))
        if len(residuals) > 1 else 0.0,
        "median": float(np.median(residuals)),
        "min": float(np.min(residuals)),
        "max": float(np.max(residuals)),
    }


def calculate_vif(
    X: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate Variance Inflation Factors.

    X should contain numeric predictor columns,
    without an intercept column.
    """

    from statsmodels.tools.tools import add_constant

    X = X.astype(float)

    if X.isna().any().any():
        raise ValueError("X contains missing values")

    X_const = add_constant(
        X,
        has_constant="add",
    )

    vif_data = []

    for i, column in enumerate(X.columns, start=1):

        vif = variance_inflation_factor(
            X_const.to_numpy(),
            i,
        )

        vif_data.append({
            "feature": column,
            "vif": float(vif),
        })

    return pd.DataFrame(vif_data)


def breusch_pagan_test(
    residuals: np.ndarray,
    X: pd.DataFrame,
) -> dict[str, float]:
    """
    Test for heteroskedasticity.

    The null hypothesis is constant error variance.
    """

    from statsmodels.tools.tools import add_constant

    residuals = np.asarray(residuals).ravel()

    X_const = add_constant(
        X.astype(float),
        has_constant="add",
    )

    lm_stat, lm_pvalue, f_stat, f_pvalue = (
        het_breuschpagan(
            residuals,
            X_const,
        )
    )

    return {
        "lm_statistic": float(lm_stat),
        "lm_pvalue": float(lm_pvalue),
        "f_statistic": float(f_stat),
        "f_pvalue": float(f_pvalue),
    }


def durbin_watson_test(
    residuals: np.ndarray,
) -> float:
    """
    Calculate the Durbin-Watson statistic.

    Values near 2 indicate little first-order
    residual autocorrelation.
    """

    return float(
        durbin_watson(
            np.asarray(residuals).ravel()
        )
    )


def ljung_box_test(
    residuals: np.ndarray,
    lags: int = 10,
) -> pd.DataFrame:
    """
    Test residual autocorrelation across multiple lags.
    """

    return acorr_ljungbox(
        np.asarray(residuals).ravel(),
        lags=[lags],
        return_df=True,
    )


def jarque_bera_test(
    residuals: np.ndarray,
) -> dict[str, float]:
    """
    Test residual normality.
    """

    jb_stat, pvalue, skew, kurtosis = jarque_bera(
        np.asarray(residuals).ravel()
    )

    return {
        "statistic": float(jb_stat),
        "pvalue": float(pvalue),
        "skewness": float(skew),
        "kurtosis": float(kurtosis),
    }


def pca_diagnostics(
    pca: PCA,
) -> pd.DataFrame:
    """
    Summarize PCA explained variance.

    PCA must already be fitted.
    """

    explained = pca.explained_variance_ratio_

    return pd.DataFrame({
        "component": np.arange(
            1,
            len(explained) + 1,
        ),
        "explained_variance_ratio": explained,
        "cumulative_explained_variance": (
            np.cumsum(explained)
        ),
    })


def diagnostic_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    X: pd.DataFrame,
    lags: int = 10,
) -> dict[str, Any]:
    """
    Generate a combined regression diagnostic report.

    X must contain the exact design-matrix predictors
    used to fit the model, excluding the intercept.
    """

    residuals = calculate_residuals(
        y_true,
        y_pred,
    )

    return {
        "performance": regression_metrics(
            y_true,
            y_pred,
        ),
        "residual_summary": residual_summary(
            residuals,
        ),
        "vif": calculate_vif(X),
        "breusch_pagan": breusch_pagan_test(
            residuals,
            X,
        ),
        "durbin_watson": durbin_watson_test(
            residuals,
        ),
        "ljung_box": ljung_box_test(
            residuals,
            lags=lags,
        ),
        "jarque_bera": jarque_bera_test(
            residuals,
        ),
    }

