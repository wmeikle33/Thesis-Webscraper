
"""
Model interpretation utilities for Thesis-Webscraper.

Interpret PCA loadings, principal component regression
coefficients, and relationships between EV discussion
features and financial returns.
"""

from typing import Any

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from statsmodels.regression.linear_model import (
    RegressionResultsWrapper,
)


def get_pca_loadings(
    pca: PCA,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Extract PCA component coefficients.

    Rows represent original features.
    Columns represent principal components.

    Note: These are component weights, sometimes
    called loadings. Correlation-based PCA loadings
    use a different scaling.
    """

    if not hasattr(pca, "components_"):
        raise ValueError("PCA must be fitted first")

    if len(feature_names) != pca.n_features_in_:
        raise ValueError(
            "Feature count does not match fitted PCA"
        )

    component_names = [
        f"PC{i + 1}"
        for i in range(pca.n_components_)
    ]

    return pd.DataFrame(
        pca.components_.T,
        index=feature_names,
        columns=component_names,
    )


def get_top_features(
    loadings: pd.DataFrame,
    component: str = "PC1",
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Identify features with the largest absolute
    component weights.
    """

    if component not in loadings.columns:
        raise KeyError(
            f"Unknown component: {component}"
        )

    if top_n < 1:
        raise ValueError("top_n must be positive")

    result = pd.DataFrame({
        "feature": loadings.index,
        "weight": loadings[component].to_numpy(),
    })

    result["absolute_weight"] = (
        result["weight"].abs()
    )

    return (
        result.sort_values(
            "absolute_weight",
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def interpret_regression(
    model: RegressionResultsWrapper,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Summarize fitted statsmodels regression results.

    Statistical significance depends on the model's
    covariance assumptions and specification.
    """

    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")

    intervals = model.conf_int(alpha=alpha)

    result = pd.DataFrame({
        "feature": model.model.exog_names,
        "coefficient": np.asarray(model.params),
        "std_error": np.asarray(model.bse),
        "t_statistic": np.asarray(model.tvalues),
        "p_value": np.asarray(model.pvalues),
        "ci_lower": np.asarray(intervals)[:, 0],
        "ci_upper": np.asarray(intervals)[:, 1],
    })

    result["significant"] = (
        result["p_value"] < alpha
    )

    result["direction"] = np.select(
        [
            result["coefficient"] > 0,
            result["coefficient"] < 0,
        ],
        [
            "positive",
            "negative",
        ],
        default="zero",
    )

    return result


def calculate_feature_effects(
    pca: PCA,
    pc_coefficients: np.ndarray,
    feature_names: list[str],
    scaler=None,
) -> pd.DataFrame:
    """
    Map PCR slopes back to original features.

    If PCA was fitted on standardized X, the
    coefficients are initially in standardized
    feature units.

    Supply the fitted scaler to convert slopes
    into original feature units.
    """

    coefficients = np.asarray(
        pc_coefficients,
        dtype=float,
    ).ravel()

    if len(coefficients) != pca.n_components_:
        raise ValueError(
            "Coefficient count must match PCA components"
        )

    effects = pca.components_.T @ coefficients

    if scaler is not None:
        scales = np.asarray(scaler.scale_)

        if len(scales) != len(effects):
            raise ValueError(
                "Scaler dimension mismatch"
            )

        effects = effects / scales

    return pd.DataFrame({
        "feature": feature_names,
        "coefficient": effects,
        "absolute_coefficient": np.abs(effects),
    }).sort_values(
        "absolute_coefficient",
        ascending=False,
    ).reset_index(drop=True)


def calculate_feature_correlations(
    X: pd.DataFrame,
    y: pd.Series,
) -> pd.DataFrame:
    """
    Calculate Pearson correlations between
    numerical features and the target variable.
    """

    if len(X) != len(y):
        raise ValueError(
            "X and y must have equal lengths"
        )

    data = X.reset_index(drop=True).copy()

    data["_target"] = pd.Series(y).reset_index(
        drop=True
    )

    correlations = data.corr(
        numeric_only=True
    )["_target"].drop("_target")

    return pd.DataFrame({
        "feature": correlations.index,
        "correlation": correlations.values,
    }).sort_values(
        "correlation",
        key=lambda values: values.abs(),
        ascending=False,
    ).reset_index(drop=True)


def generate_interpretation_report(
    pca: PCA,
    feature_names: list[str],
    regression_model: RegressionResultsWrapper,
    X: pd.DataFrame | None = None,
    y: pd.Series | None = None,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """
    Generate a combined PCA and regression
    interpretation report.
    """

    loadings = get_pca_loadings(
        pca,
        feature_names,
    )

    component_summaries = {}

    for component in loadings.columns:
        component_summaries[component] = (
            get_top_features(
                loadings,
                component=component,
            )
        )

    report = {
        "pca_loadings": loadings,
        "top_features": component_summaries,
        "regression": interpret_regression(
            regression_model,
            alpha=alpha,
        ),
        "explained_variance": (
            pca.explained_variance_ratio_.tolist()
        ),
    }

    if X is not None and y is not None:
        report["feature_correlations"] = (
            calculate_feature_correlations(X, y)
        )

    return report

