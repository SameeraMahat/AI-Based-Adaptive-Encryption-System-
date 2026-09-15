import os
import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

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
# LOAD MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Random Forest model not found: {MODEL_PATH}"
    )

if not os.path.exists(ENCODER_PATH):
    raise FileNotFoundError(
        f"Label encoders not found: {ENCODER_PATH}"
    )


model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "file_type",
    "file_size_mb",
    "document_category",
    "pii_count",
    "category_confidence",
    "confidential_marker",
    "sensitivity_score"
]


# ============================================================
# PREDICTION
# ============================================================

def predict_encryption_algorithm(features):

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            f"Missing prediction features: {missing_features}"
        )

    input_data = {}

    for feature in FEATURE_COLUMNS:
        input_data[feature] = features[feature]

    categorical_columns = [
        "file_type",
        "document_category",
        "confidential_marker"
    ]

    for column in categorical_columns:

        encoder = encoders[column]

        value = str(input_data[column])

        if value not in encoder.classes_:
            raise ValueError(
                f"Unknown value '{value}' for {column}. "
                f"Known values: {list(encoder.classes_)}"
            )

        input_data[column] = encoder.transform(
            [value]
        )[0]

    X = pd.DataFrame(
        [input_data],
        columns=FEATURE_COLUMNS
    )

    prediction_encoded = model.predict(X)[0]

    target_encoder = encoders["algorithm"]

    algorithm = target_encoder.inverse_transform(
        [prediction_encoded]
    )[0]

    probabilities = model.predict_proba(X)[0]

    confidence = float(max(probabilities))

    return {
        "algorithm": algorithm,
        "confidence": round(confidence, 4)
    }