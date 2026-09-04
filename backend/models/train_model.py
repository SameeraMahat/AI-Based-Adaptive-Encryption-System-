import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "encryption_dataset_v2.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "encryption_model.pkl"
)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

print("\nLoading encryption dataset...")

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

print(f"Dataset shape: {df.shape}")


# --------------------------------------------------
# VALIDATE DATASET
# --------------------------------------------------

required_columns = [
    "file_type",
    "file_size_mb",
    "cpu_usage",
    "ram_usage",
    "pii_count",
    "document_category",
    "category_confidence",
    "confidential_marker",
    "sensitivity_score",
    "algorithm"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# --------------------------------------------------
# FEATURES AND TARGET
# --------------------------------------------------

FEATURE_COLUMNS = [
    "file_type",
    "file_size_mb",
    "cpu_usage",
    "ram_usage",
    "pii_count",
    "document_category",
    "category_confidence",
    "confidential_marker",
    "sensitivity_score"
]

TARGET_COLUMN = "algorithm"


X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]


# --------------------------------------------------
# DISPLAY DATASET INFORMATION
# --------------------------------------------------

print("\nFeatures used by the model:")

for feature in FEATURE_COLUMNS:
    print(f"  - {feature}")

print("\nTarget classes:")

for target, count in y.value_counts().items():
    print(f"  - {target}: {count}")


# --------------------------------------------------
# CATEGORICAL AND NUMERICAL FEATURES
# --------------------------------------------------

CATEGORICAL_FEATURES = [
    "file_type",
    "document_category",
    "confidential_marker"
]

NUMERICAL_FEATURES = [
    "file_size_mb",
    "cpu_usage",
    "ram_usage",
    "pii_count",
    "category_confidence",
    "sensitivity_score"
]


# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES
        ),
        (
            "numerical",
            "passthrough",
            NUMERICAL_FEATURES
        )
    ]
)


# --------------------------------------------------
# RANDOM FOREST MODEL
# --------------------------------------------------

random_forest = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# --------------------------------------------------
# COMPLETE ML PIPELINE
# --------------------------------------------------

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            random_forest
        )
    ]
)


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(
    f"\nTraining samples: {len(X_train)}"
)

print(
    f"Testing samples: {len(X_test)}"
)


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

print("\nTraining Random Forest model...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(
    f"\nModel Accuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print(
    f"\nModel saved successfully:"
)

print(
    MODEL_PATH
)

print("\nTraining pipeline completed successfully.")