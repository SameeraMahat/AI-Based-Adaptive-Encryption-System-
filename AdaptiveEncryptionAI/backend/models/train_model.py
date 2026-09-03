import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "encryption_dataset_v2.csv"
)

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "rf_model.pkl"
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "label_encoders.pkl"
)


# ============================================================
# CONFIGURATION
# ============================================================

# IMPORTANT:
# CPU and RAM are NOT used because they describe machine state,
# not document characteristics.

FEATURE_COLUMNS = [
    "file_type",
    "file_size_mb",
    "document_category",
    "pii_count",
    "category_confidence",
    "confidential_marker",
    "sensitivity_score"
]

TARGET_COLUMN = "algorithm"

CATEGORICAL_COLUMNS = [
    "file_type",
    "document_category",
    "confidential_marker"
]


# ============================================================
# LOAD DATASET
# ============================================================

print("\n================================")
print("LOADING DATASET")
print("================================")

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully.")
print("Dataset shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())


# ============================================================
# DATASET INFORMATION
# ============================================================

print("\n================================")
print("DATASET COLUMNS")
print("================================")

print(df.columns.tolist())

print("\nAlgorithm distribution:")
print(df[TARGET_COLUMN].value_counts())


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# SELECT FEATURES AND TARGET
# ============================================================

X = df[FEATURE_COLUMNS].copy()
y = df[TARGET_COLUMN].copy()


# ============================================================
# DATA CLEANING
# ============================================================

print("\n================================")
print("DATA CLEANING")
print("================================")

rows_before = len(X)

# Remove rows where target is missing
valid_rows = y.notna()

X = X.loc[valid_rows].copy()
y = y.loc[valid_rows].copy()

# Remove rows where required features are missing
valid_rows = X.notna().all(axis=1)

X = X.loc[valid_rows].copy()
y = y.loc[valid_rows].copy()

print("Rows before cleaning:", rows_before)
print("Rows after cleaning :", len(X))


# ============================================================
# FIX DATA TYPES
# ============================================================

# Convert numeric columns explicitly.

NUMERIC_COLUMNS = [
    "file_size_mb",
    "pii_count",
    "category_confidence",
    "sensitivity_score"
]

for column in NUMERIC_COLUMNS:
    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )

# Remove rows that became invalid after numeric conversion.
valid_rows = X[NUMERIC_COLUMNS].notna().all(axis=1)

X = X.loc[valid_rows].copy()
y = y.loc[valid_rows].copy()


# ============================================================
# ENCODE CATEGORICAL FEATURES
# ============================================================

print("\n================================")
print("ENCODING CATEGORICAL FEATURES")
print("================================")

encoders = {}

for column in CATEGORICAL_COLUMNS:

    encoder = LabelEncoder()

    # Convert source column to string first.
    values = X[column].astype(str)

    # Encode to integers.
    encoded_values = encoder.fit_transform(values)

    # IMPORTANT:
    # Assign a numeric Series instead of assigning integers
    # directly into pandas StringDtype column.
    X[column] = pd.Series(
        encoded_values,
        index=X.index,
        dtype="int64"
    )

    encoders[column] = encoder

    print(f"\n{column}:")
    for index, value in enumerate(encoder.classes_):
        print(f"  {index} = {value}")


# ============================================================
# ENCODE TARGET
# ============================================================

print("\n================================")
print("ENCODING TARGET")
print("================================")

target_encoder = LabelEncoder()

y_encoded = target_encoder.fit_transform(
    y.astype(str)
)

encoders["algorithm"] = target_encoder

print("\nAlgorithm classes:")

for index, algorithm in enumerate(
    target_encoder.classes_
):
    print(f"  {index} = {algorithm}")


# ============================================================
# FINAL FEATURE CHECK
# ============================================================

print("\n================================")
print("FINAL FEATURES")
print("================================")

print(X.dtypes)

print("\nFeature columns:")
for column in FEATURE_COLUMNS:
    print("-", column)

print("\nTarget:")
print("-", TARGET_COLUMN)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\n================================")
print("TRAIN / TEST SPLIT")
print("================================")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("Training samples:", len(X_train))
print("Testing samples :", len(X_test))


# ============================================================
# RANDOM FOREST
# ============================================================

print("\n================================")
print("RANDOM FOREST TRAINING")
print("================================")

model = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)
print("Training Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# MODEL EVALUATION
# ============================================================

print("\n================================")
print("MODEL EVALUATION")
print("================================")

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(f"Accuracy: {accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=target_encoder.classes_,
        zero_division=0
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n================================")
print("FEATURE IMPORTANCE")
print("================================")

feature_importance = pd.DataFrame({
    "feature": FEATURE_COLUMNS,
    "importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print(feature_importance.to_string(index=False))


# ============================================================
# SAVE MODEL
# ============================================================

print("\n================================")
print("SAVING MODEL")
print("================================")

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    encoders,
    ENCODER_PATH
)

print("Model saved to:")
print(MODEL_PATH)

print("\nEncoders saved to:")
print(ENCODER_PATH)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n================================")
print("TRAINING COMPLETE")
print("================================")

print(f"Dataset rows      : {len(X)}")
print(f"Training samples  : {len(X_train)}")
print(f"Testing samples   : {len(X_test)}")
print(f"Accuracy          : {accuracy:.4f}")

print("\nPredicted algorithms:")

for algorithm in target_encoder.classes_:
    print("-", algorithm)

print("\nGenerated files:")

print("-", MODEL_PATH)
print("-", ENCODER_PATH)