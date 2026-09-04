def calculate_sensitivity(
    features,
    classification,
    system_features
):
    """
    Prepare sensitivity-related features for the ML model.

    The provided dataset contains a sensitivity_score column,
    but its original calculation formula is not documented.

    Therefore, this project uses a deterministic runtime score
    based on detected PII, confidential keywords, and
    confidential markers.
    """

    # --------------------------------
    # PII COUNT
    # --------------------------------

    pii_count = (
        features.get("email_count", 0)
        + features.get("phone_count", 0)
        + features.get("pan_count", 0)
        + features.get("aadhaar_count", 0)
    )

    # --------------------------------
    # CONFIDENTIAL KEYWORDS
    # --------------------------------

    confidential_keyword_count = features.get(
        "confidential_keyword_count",
        0
    )

    # --------------------------------
    # CONFIDENTIAL MARKER
    # --------------------------------

    confidential_marker = (
        "Yes"
        if confidential_keyword_count > 0
        else "No"
    )

    # --------------------------------
    # RUNTIME SENSITIVITY SCORE
    # --------------------------------

    # PII contributes up to 70 points
    pii_component = min(
        pii_count / 15,
        1
    ) * 70

    # Confidential keywords contribute up to 20 points
    keyword_component = min(
        confidential_keyword_count / 10,
        1
    ) * 20

    # Confidential marker contributes 10 points
    marker_component = (
        10
        if confidential_marker == "Yes"
        else 0
    )

    sensitivity_score = min(
        round(
            pii_component
            + keyword_component
            + marker_component,
            2
        ),
        100
    )

    # --------------------------------
    # RETURN FEATURES
    # --------------------------------

    return {

        # PII
        "pii_count": pii_count,

        "email_count":
            features.get("email_count", 0),

        "phone_count":
            features.get("phone_count", 0),

        "pan_count":
            features.get("pan_count", 0),

        "aadhaar_count":
            features.get("aadhaar_count", 0),

        # Classification
        "document_category":
            classification["document_category"],

        "category_confidence":
            classification["category_confidence"],

        # Text features
        "word_count":
            features.get("word_count", 0),

        "character_count":
            features.get("character_count", 0),

        "sentence_count":
            features.get("sentence_count", 0),

        "confidential_keyword_count":
            confidential_keyword_count,

        # Sensitivity
        "confidential_marker":
            confidential_marker,

        "sensitivity_score":
            sensitivity_score,

        # File information
        "file_size_bytes":
            system_features["file_size_bytes"],

        "file_size_mb":
            system_features["file_size_mb"],

        "file_extension":
            system_features["file_extension"]
    }