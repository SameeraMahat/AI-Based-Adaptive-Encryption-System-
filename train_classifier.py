"""
Trains the sensitivity classifier for the AI-Based Adaptive Encryption System.

Reads: ../data/labeled_dataset.csv
Outputs: model.pkl, file_type_encoder.pkl, keyword_vectorizer.pkl

Features used:
- file_type (one-hot encoded)
- size_kb (numeric)
- keyword_count (numeric)
- keywords_present (multi-hot encoded via CountVectorizer)

Label: sensitivity_label (Low / Medium / High / Critical)

Run: python train_classifier.py
"""

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import scipy.sparse as sp

DATA_PATH = "../data/labeled_dataset.csv"


def build_features(df, file_type_encoder=None, keyword_vectorizer=None, fit=True):
    """Turns raw dataset columns into a numeric feature matrix."""

    # --- file_type: one-hot encode ---
    file_type_col = df[["file_type"]]
    if fit:
        file_type_encoder = OneHotEncoder(handle_unknown="ignore")
        file_type_encoded = file_type_encoder.fit_transform(file_type_col)
    else:
        file_type_encoded = file_type_encoder.transform(file_type_col)

    # --- keywords_present: treat as space-joined tokens, multi-hot encode ---
    keyword_text = df["keywords_present"].str.replace(";", " ")
    if fit:
        keyword_vectorizer = CountVectorizer(binary=True)
        keyword_encoded = keyword_vectorizer.fit_transform(keyword_text)
    else:
        keyword_encoded = keyword_vectorizer.transform(keyword_text)

    # --- numeric features ---
    numeric = df[["size_kb", "keyword_count"]].to_numpy()
    numeric_sparse = sp.csr_matrix(numeric)

    # --- combine all ---
    X = sp.hstack([file_type_encoded, keyword_encoded, numeric_sparse]).tocsr()

    return X, file_type_encoder, keyword_vectorizer


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows")
    print(df["sensitivity_label"].value_counts(), "\n")

    y = df["sensitivity_label"]

    # Build features (fit encoders on full data's vocabulary, then split)
    X, file_type_encoder, keyword_vectorizer = build_features(df, fit=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- Hyperparameter tuning via grid search (5-fold CV on training data) ---
    param_grid = {
        "n_estimators": [100, 200, 300],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 4],
    }
    base_clf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(base_clf, param_grid, cv=5, scoring="accuracy", n_jobs=-1)
    grid_search.fit(X_train, y_train)

    print(f"Best params: {grid_search.best_params_}")
    print(f"Best CV accuracy (on training folds): {grid_search.best_score_:.2%}\n")

    clf = grid_search.best_estimator_

    # --- Cross-validated score on full training set (more reliable than one split) ---
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    print(f"5-fold CV accuracy (best model): {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})\n")

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"Held-out test accuracy: {acc:.2%}\n")
    print("Classification report:")
    print(classification_report(y_test, y_pred))

    # Feature importance sanity check
    print("Top feature importances (index-based, informational only):")
    importances = clf.feature_importances_
    top_idx = np.argsort(importances)[::-1][:10]
    print(top_idx, importances[top_idx])

    # --- Save model + encoders so the API can reuse them without retraining ---
    joblib.dump(clf, "model.pkl")
    joblib.dump(file_type_encoder, "file_type_encoder.pkl")
    joblib.dump(keyword_vectorizer, "keyword_vectorizer.pkl")
    print("\nSaved model.pkl, file_type_encoder.pkl, keyword_vectorizer.pkl")


if __name__ == "__main__":
    main()
