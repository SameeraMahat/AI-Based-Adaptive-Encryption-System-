
import re

CONFIDENTIAL_KEYWORDS = [
    "confidential",
    "secret",
    "salary",
    "employee",
    "private",
    "classified",
    "restricted",
    "internal",
]


def extract_file_features(text, pii):
    """
    Extract numerical features from document text.

    Confidential keyword count:
    - Counts whole-word occurrences.
    - Counts repeated occurrences.
    - Does not count substring matches.

    Confidential marker:
    - Detects explicit classification labels.
    - Supports optional suffixes such as '- INTERNAL USE'.
    """

    if not isinstance(text, str):
        text = ""

    if not isinstance(pii, dict):
        pii = {}

    words = text.split()
    sentences = re.split(r"[.!?]+", text)
    text_lower = text.casefold()

    # Count whole-word occurrences of confidential keywords.
    keyword_count = 0

    for keyword in CONFIDENTIAL_KEYWORDS:
        pattern = r"\b" + re.escape(keyword.casefold()) + r"\b"
        keyword_count += len(re.findall(pattern, text_lower))

    # Safely count detected PII values.
    def safe_count(key):
        value = pii.get(key, [])

        if value is None:
            return 0

        if isinstance(value, (list, tuple, set)):
            return len(value)

        return 0

    features = {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len(
    [sentence for sentence in sentences if sentence.strip()]
),
        "email_count": safe_count("emails"),
        "phone_count": safe_count("phone_numbers"),
        "aadhaar_count": safe_count("aadhaar_numbers"),
        "pan_count": safe_count("pan_numbers"),
        "confidential_keyword_count": keyword_count,
    }

    # Detect explicit classification labels.
    # Examples:
    # CLASSIFICATION: CONFIDENTIAL
    # Classification: Restricted
    # SECURITY CLASSIFICATION: CONFIDENTIAL - INTERNAL USE
    marker_pattern = (
        r"(?im)^\s*"
        r"(?:classification|security classification)"
        r"\s*:\s*"
        r"(?:confidential|classified|restricted)"
        r"(?:\s*[-—:]\s*.*)?"
        r"\s*$"
    )

    features["confidential_marker"] = bool(
        re.search(marker_pattern, text)
    )

    return features