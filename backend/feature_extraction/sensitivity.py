
def calculate_sensitivity(features, classification, system_features):
    """
    Calculate a sensitivity score from 0 to 100.

    Components:
    - PII: up to 50 points
    - Confidential keywords: up to 25 points
    - Explicit confidential marker: 10 points
    - Document category: up to 15 points
    """

    features = features if isinstance(features, dict) else {}
    classification = classification if isinstance(classification, dict) else {}
    system_features = system_features if isinstance(system_features, dict) else {}

    def safe_nonnegative_int(value):
        try:
            return max(0, int(value or 0))
        except (ValueError, TypeError, OverflowError):
            return 0

    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError, OverflowError):
            return default

    # PII counts
    pii_keys = [
        "email_count",
        "phone_count",
        "pan_count",
        "aadhaar_count",
    ]

    counts = {
        key: safe_nonnegative_int(features.get(key, 0))
        for key in pii_keys
    }

    pii_count = sum(counts.values())

    # Confidential keyword count
    confidential_keyword_count = safe_nonnegative_int(
        features.get("confidential_keyword_count", 0)
    )

    # Document category and confidence
    document_category = str(
        classification.get("document_category", "General") or "General"
    ).strip()

    category_confidence = max(
        0.0,
        min(
            safe_float(classification.get("category_confidence", 0.0)),
            1.0,
        ),
    )

    normalized_category = document_category.casefold()

    # Align with category names returned by classifier.py
    category_weights = {
        "personal": 8,
        "business": 10,
        "hr": 12,
        "finance": 15,
        "financial": 15,
        "legal": 15,
        "medical": 15,
        "research": 8,
        "internal": 12,
        "confidential": 15,
    }

    category_base = category_weights.get(normalized_category, 0)
    category_component = category_base * category_confidence

    # Use the explicit marker from file_features.py.
    # Do not infer a marker just because a keyword exists.
    marker_value = features.get("confidential_marker", False)

    if isinstance(marker_value, str):
        has_confidential_marker = (
            marker_value.strip().casefold()
            in {"yes", "true", "1"}
        )
    else:
        has_confidential_marker = marker_value is True

    confidential_marker = "Yes" if has_confidential_marker else "No"

    # Score components
    pii_component = min((pii_count / 15) * 50, 50)

    keyword_component = min(
        (confidential_keyword_count / 10) * 25,
        25,
    )

    marker_component = 10 if has_confidential_marker else 0

    sensitivity_score = round(
        min(
            pii_component
            + keyword_component
            + marker_component
            + category_component,
            100,
        ),
        2,
    )

    # Safe file metadata defaults
    file_size_bytes = safe_nonnegative_int(
        system_features.get("file_size_bytes", 0)
    )
    file_size_mb = safe_float(
        system_features.get("file_size_mb", file_size_bytes / (1024 * 1024))
    )
    file_extension = system_features.get("file_extension", "")

    return {
        "pii_count": pii_count,
        "email_count": counts["email_count"],
        "phone_count": counts["phone_count"],
        "pan_count": counts["pan_count"],
        "aadhaar_count": counts["aadhaar_count"],
        "document_category": document_category,
        "category_confidence": category_confidence,
        "word_count": safe_nonnegative_int(features.get("word_count", 0)),
        "character_count": safe_nonnegative_int(features.get("character_count", 0)),
        "sentence_count": safe_nonnegative_int(features.get("sentence_count", 0)),
        "confidential_keyword_count": confidential_keyword_count,
        "confidential_marker": confidential_marker,
        "sensitivity_score": sensitivity_score,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "file_extension": file_extension,
    }
