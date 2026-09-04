def select_encryption_policy(classification, sensitivity):
    """
    Adaptive encryption policy.

    Selects an encryption algorithm based on:

        - document category
        - PII count
        - confidential keywords
        - file size
        - file type
    """

    category = classification.get(
        "document_category",
        "General"
    )

    pii_count = sensitivity.get(
        "pii_count",
        0
    )

    confidential_keywords = sensitivity.get(
        "confidential_keyword_count",
        0
    )

    file_size = sensitivity.get(
        "file_size_bytes",
        0
    )

    file_extension = sensitivity.get(
        "file_extension",
        ""
    ).lower()

    # --------------------------------
    # HIGHLY SENSITIVE DOCUMENTS
    # --------------------------------

    highly_sensitive = (
        category in [
            "Medical",
            "Legal",
            "Finance",
            "HR"
        ]
        or pii_count >= 2
        or confidential_keywords >= 2
    )

    # --------------------------------
    # HYBRID ENCRYPTION
    # --------------------------------
    #
    # Used when a file is both:
    #   1. highly sensitive
    #   2. relatively large
    #
    # Hybrid encryption uses AES-256-GCM
    # for the file and RSA-OAEP to protect
    # the AES session key.

    if highly_sensitive and file_size >= 5 * 1024 * 1024:

        return {
            "algorithm": "Hybrid",
            "security_level": "Very High",
            "reason": (
                "Large highly-sensitive file selected "
                "for hybrid AES-256-GCM + RSA-OAEP encryption."
            )
        }

    # --------------------------------
    # HIGH SECURITY
    # --------------------------------

    if highly_sensitive:

        return {
            "algorithm": "AES-256-GCM",
            "security_level": "High",
            "reason": (
                "Highly sensitive document detected; "
                "AES-256-GCM selected for authenticated encryption."
            )
        }

    # --------------------------------
    # FAST ENCRYPTION
    # --------------------------------

    if file_extension in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        return {
            "algorithm": "ChaCha20",
            "security_level": "Medium",
            "reason": (
                "Image file selected for lightweight "
                "ChaCha20 encryption."
            )
        }

    # --------------------------------
    # GENERAL DOCUMENTS
    # --------------------------------

    return {
        "algorithm": "ChaCha20",
        "security_level": "Standard",
        "reason": (
            "General document selected for lightweight "
            "adaptive encryption."
        )
    }