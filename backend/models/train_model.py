import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "encryption_dataset_adaptive.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "encryption_model.pkl"
)


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "sensitivity_score",
    "file_size_mb"
]

TARGET_COLUMN = "algorithm"


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("=" * 60)
print("ADAPTIVE ENCRYPTION ML TRAINING")
print("=" * 60)

print()
print("Dataset:")
print(DATASET_PATH)


if not os.path.exists(DATASET_PATH):

    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )


df = pd.read_csv(
    DATASET_PATH
)


# ============================================================
# DATASET INFORMATION
# ============================================================

print()
print("Dataset Shape:")
print(df.shape)

print()
print("Dataset Columns:")
print(list(df.columns))


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = (
    FEATURE_COLUMNS
    + [TARGET_COLUMN]
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    raise ValueError(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )


# ============================================================
# CLEAN DATA
# ============================================================

df = df[
    required_columns
].copy()


df["sensitivity_score"] = pd.to_numeric(
    df["sensitivity_score"],
    errors="coerce"
)

df["file_size_mb"] = pd.to_numeric(
    df["file_size_mb"],
    errors="coerce"
)


df = df.dropna()


# ============================================================
# DISPLAY ALGORITHM DISTRIBUTION
# ============================================================

print()
print("Algorithm Distribution:")
print(
    df[TARGET_COLUMN]
    .value_counts()
)


# ============================================================
# DISPLAY ADAPTIVE RULE
# ============================================================

print()
print("-" * 60)
print("ADAPTIVE ENCRYPTION RULE")
print("-" * 60)

print(
    "Sensitivity <= 20              -> ChaCha20"
)

print(
    "Sensitivity 21-50              -> AES"
)

print(
    "Sensitivity > 50 + Size >= 5MB -> Hybrid"
)

print(
    "Sensitivity > 50 + Size < 5MB  -> AES"
)


# ============================================================
# FEATURES AND TARGET
# ============================================================

X = df[
    FEATURE_COLUMNS
]

y = df[
    TARGET_COLUMN
]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print()
print("Training Samples:")
print(len(X_train))

print()
print("Testing Samples:")
print(len(X_test))


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

model = RandomForestClassifier(

    n_estimators=300,

    max_depth=12,

    min_samples_leaf=1,

    random_state=42,

    class_weight="balanced",

    n_jobs=-1
)


# ============================================================
# TRAIN MODEL
# ============================================================

print()
print("-" * 60)
print("TRAINING RANDOM FOREST")
print("-" * 60)

model.fit(
    X_train,
    y_train
)


print("Training completed.")


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(
    X_test
)


# ============================================================
# PROBABILITIES
# ============================================================

y_probability = model.predict_proba(
    X_test
)


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


balanced_accuracy = balanced_accuracy_score(
    y_test,
    y_pred
)


macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro"
)


print()
print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print()
print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    f"Balanced Accuracy: {balanced_accuracy:.4f}"
)

print(
    f"Macro F1 Score: {macro_f1:.4f}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print()
print("Classification Report:")
print()

print(
    classification_report(
        y_test,
        y_pred,
        digits=4
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print()
print("Confusion Matrix:")
print()

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print()
print("-" * 60)
print("FEATURE IMPORTANCE")
print("-" * 60)

feature_importance = pd.DataFrame({

    "feature":
        FEATURE_COLUMNS,

    "importance":
        model.feature_importances_

})


feature_importance = (
    feature_importance
    .sort_values(
        by="importance",
        ascending=False
    )
)


print(
    feature_importance.to_string(
        index=False
    )
)


# ============================================================
# MODEL CLASSES
# ============================================================

print()
print("Model Classes:")

print(
    model.classes_
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)


print()
print("=" * 60)
print("MODEL SAVED")
print("=" * 60)

print()
print(
    f"Saved to: {MODEL_PATH}"
)

print()
print("Training completed successfully.")
print()