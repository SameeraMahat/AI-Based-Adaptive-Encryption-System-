import re


def detect_pii(text):
    """
    Detect common Personally Identifiable Information (PII)
    from extracted document text.
    """

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    phone_pattern = r"(?:\+91[-\s]?)?[6-9]\d{9}"

    aadhaar_pattern = r"\b\d{4}\s?\d{4}\s?\d{4}\b"

    pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

    pii = {
        "emails": list(set(re.findall(email_pattern, text))),
        "phone_numbers": list(set(re.findall(phone_pattern, text))),
        "aadhaar_numbers": list(set(re.findall(aadhaar_pattern, text))),
        "pan_numbers": list(set(re.findall(pan_pattern, text)))
    }

    return pii