import pandas as pd
import numpy as np


def get_feature_importance(model, feature_names):
    """
    Extract feature importance from:
    - Tree models (RandomForest, XGBoost)
    - Linear models (Logistic Regression)
    """

    importance = None

    # Tree-based models
    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_

    # Linear models
    elif hasattr(model, "coef_"):
        importance = np.abs(model.coef_[0])

    else:
        return []

    # Safety check (VERY IMPORTANT)
    if len(importance) != len(feature_names):
        return []

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": importance
    })

    df = df.sort_values(by="importance", ascending=False)

    # Normalize (optional but good for UI)
    df["importance"] = df["importance"] / df["importance"].sum()

    return df.to_dict(orient="records")