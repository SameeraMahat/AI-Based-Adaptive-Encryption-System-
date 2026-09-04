import re

CONFIDENTIAL_KEYWORDS = [
    "confidential",
    "secret",
    "salary",
    "employee",
    "private",
    "classified",
    "restricted",
    "internal"
]


def extract_file_features(text, pii):
    """
    Extract numerical features from the document text.
    """

    words = text.split()

    sentences = re.split(r"[.!?]+", text)

    keyword_count = 0

    text_lower = text.lower()

    for keyword in CONFIDENTIAL_KEYWORDS:
        keyword_count += text_lower.count(keyword)

    features = {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "email_count": len(pii["emails"]),
        "phone_count": len(pii["phone_numbers"]),
        "aadhaar_count": len(pii["aadhaar_numbers"]),
        "pan_count": len(pii["pan_numbers"]),
        "confidential_keyword_count": keyword_count
    }

    return features