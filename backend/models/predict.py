import os
import joblib
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

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


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model = joblib.load(
    MODEL_PATH
)


# ============================================================
# FEATURES USED BY THE ML MODEL
# ============================================================

FEATURE_COLUMNS = [
    "sensitivity_score",
    "file_size_mb"
]


# ============================================================
# DISPLAY NAMES
# ============================================================

ALGORITHM_DISPLAY_NAMES = {

    "AES":
        "AES-256-GCM",

    "ChaCha20":
        "ChaCha20-Poly1305",

    "Hybrid":
        "Hybrid AES-256-GCM + RSA-OAEP"

}


# ============================================================
# ML PREDICTION FUNCTION
# ============================================================

def predict_encryption(
    features,
    classification,
    sensitivity,
    system_features
):
    """
    Predict the encryption algorithm using
    the trained Random Forest model.

    The encryption-decision model uses:

        1. sensitivity_score
        2. file_size_mb

    These are the two features used to define
    the adaptive encryption strategy.
    """

    # ========================================================
    # PREPARE INPUT VALUES
    # ========================================================

    sensitivity_score = float(
        sensitivity.get(
            "sensitivity_score",
            0
        )
    )

    file_size_mb = float(
        system_features.get(
            "file_size_mb",
            sensitivity.get(
                "file_size_mb",
                0
            )
        )
    )


    # ========================================================
    # CREATE MODEL INPUT
    # ========================================================

    input_data = {

        "sensitivity_score":
            sensitivity_score,

        "file_size_mb":
            file_size_mb

    }


    input_df = pd.DataFrame(
        [input_data],
        columns=FEATURE_COLUMNS
    )


    # ========================================================
    # RANDOM FOREST PREDICTION
    # ========================================================

    prediction = model.predict(
        input_df
    )[0]


    # ========================================================
    # PREDICTION PROBABILITIES
    # ========================================================

    probabilities = model.predict_proba(
        input_df
    )[0]


    # ========================================================
    # MODEL CLASSES
    # ========================================================

    classes = model.classes_


    probability_data = {

        str(class_name):
            round(
                float(probability),
                4
            )

        for class_name, probability
        in zip(
            classes,
            probabilities
        )

    }


    # ========================================================
    # CONFIDENCE
    # ========================================================

    confidence = round(
        float(
            max(probabilities)
        ),
        4
    )


    # ========================================================
    # DISPLAY ALGORITHM
    # ========================================================

    display_algorithm = (
        ALGORITHM_DISPLAY_NAMES.get(
            prediction,
            str(prediction)
        )
    )


    # ========================================================
    # RETURN ML RESULT
    # ========================================================

    return {

        "algorithm":
            str(prediction),

        "display_algorithm":
            display_algorithm,

        "confidence":
            confidence,

        "probabilities":
            probability_data,

        "decision_source":
            "Random Forest ML Model",

        "input_features": {

            "sensitivity_score":
                sensitivity_score,

            "file_size_mb":
                file_size_mb

        }

    }