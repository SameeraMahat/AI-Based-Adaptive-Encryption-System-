def calculate_sensitivity(features, classification, system_features):
    """
    Extract sensitivity-related features for the ML model.

    This function does NOT decide whether a document is sensitive.
    It only prepares features that will be used by the Random Forest model.
    """

    # Total PII count
    pii_count = (
        features["email_count"] +
        features["phone_count"] +
        features["pan_count"] +
        features["aadhaar_count"]
    )

    return {
        "pii_count": pii_count,
        "document_category": classification["document_category"],
        "category_confidence": classification["category_confidence"],

        "email_count": features["email_count"],
        "phone_count": features["phone_count"],
        "pan_count": features["pan_count"],
        "aadhaar_count": features["aadhaar_count"],

        "word_count": features["word_count"],
        "character_count": features["character_count"],
        "sentence_count": features["sentence_count"],
        "confidential_keyword_count": features["confidential_keyword_count"],

        "file_size_bytes": system_features["file_size_bytes"],
        "file_extension": system_features["file_extension"]
    }