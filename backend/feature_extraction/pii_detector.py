
import re


def detect_pii(text):
    """
    Detect common PII patterns in extracted document text.

    Note:
    - Aadhaar detection checks format only, not authenticity.
    - Phone detection checks plausible Indian mobile formats only.
    - PAN detection is case-insensitive.
    """

    if not isinstance(text, str) or not text:
        return {
            "emails": [],
            "phone_numbers": [],
            "aadhaar_numbers": [],
            "pan_numbers": [],
        }

    # Email format detection
    email_pattern = (
        r"(?<![\w.+%-])"
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        r"(?![\w.-])"
    )

    # Indian mobile format:
    # optional +91 prefix, followed by a 10-digit number
    # whose first digit is 6, 7, 8, or 9.
    phone_pattern = (
        r"(?<!\d)"
        r"(?:\+91[\s-]?)?"
        r"[6-9]\d{4}[\s-]?\d{5}"
        r"(?!\d)"
    )

    # Aadhaar-like 12-digit format, optionally separated
    # into three groups of four digits.
    aadhaar_pattern = (
        r"(?<!\d)"
        r"\d{4}[ -]?\d{4}[ -]?\d{4}"
        r"(?!\d)"
    )

    # PAN format, case-insensitive.
    pan_pattern = r"(?<![A-Z0-9])[A-Z]{5}[0-9]{4}[A-Z](?![A-Z0-9])"

    emails = set(re.findall(email_pattern, text, flags=re.IGNORECASE))
    phones = set(re.findall(phone_pattern, text))
    aadhaar_numbers = set(re.findall(aadhaar_pattern, text))
    pan_numbers = set(
        match.upper()
        for match in re.findall(
            pan_pattern,
            text,
            flags=re.IGNORECASE
        )
    )

    return {
        "emails": sorted(emails, key=str.lower),
        "phone_numbers": sorted(phones),
        "aadhaar_numbers": sorted(aadhaar_numbers),
        "pan_numbers": sorted(pan_numbers),
    }
