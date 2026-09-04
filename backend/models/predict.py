import os
import joblib
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "encryption_model.pkl"
)


# Load trained Random Forest pipeline
model = joblib.load(MODEL_PATH)


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


def predict_encryption(
    features,
    classification,
    sensitivity,
    system_features
):
    """
    Predict the encryption algorithm using
    the trained Random Forest model.
    """

    # --------------------------------
    # PREPARE MODEL INPUT
    # --------------------------------

    input_data = {
        "file_type": system_features["file_type"],
        "file_size_mb": system_features["file_size_mb"],
        "cpu_usage": system_features["cpu_usage"],
        "ram_usage": system_features["ram_usage"],

        "pii_count": sensitivity["pii_count"],

        "document_category": classification["document_category"],
        "category_confidence": classification["category_confidence"],

        "confidential_marker":
            sensitivity["confidential_marker"],

        "sensitivity_score":
            sensitivity["sensitivity_score"]
    }

    # Create DataFrame using exactly
    # the same feature names as training
    input_df = pd.DataFrame(
        [input_data],
        columns=FEATURE_COLUMNS
    )

    # --------------------------------
    # ML PREDICTION
    # --------------------------------

    prediction = model.predict(input_df)[0]

    # --------------------------------
    # PREDICTION PROBABILITIES
    # --------------------------------

    probabilities = model.predict_proba(input_df)[0]

    # The trained model is a Pipeline.
    # Get the classes from its Random Forest classifier.
    classifier = model.named_steps["classifier"]

    classes = classifier.classes_

    probability_data = {
        class_name: round(
            float(probability),
            4
        )
        for class_name, probability
        in zip(classes, probabilities)
    }

    # Highest probability = model confidence
    confidence = round(
        float(max(probabilities)),
        4
    )

    # --------------------------------
    # RETURN RESULT
    # --------------------------------

    return {
        "algorithm": prediction,
        "confidence": confidence,
        "probabilities": probability_data
    }