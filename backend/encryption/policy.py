def select_encryption_policy(classification, sensitivity):
    sensitivity_score = float(
        sensitivity.get("sensitivity_score", 0)
    )

    file_size_mb = float(
        sensitivity.get("file_size_mb", 0)
    )

    # LOW SENSITIVITY
    if sensitivity_score <= 20:
        return {
            "algorithm": "ChaCha20",
            "display_algorithm": "ChaCha20-Poly1305",
            "security_level": "Low",
            "risk_level": "Low",
            "reason": (
                "Low sensitivity detected. "
                "ChaCha20-Poly1305 is selected for efficient "
                "authenticated encryption."
            )
        }

    # MEDIUM SENSITIVITY
    elif sensitivity_score <= 50:
        return {
            "algorithm": "AES",
            "display_algorithm": "AES-256-GCM",
            "security_level": "Medium",
            "risk_level": "Medium",
            "reason": (
                "Medium sensitivity detected. "
                "AES-256-GCM is selected for strong authenticated encryption."
            )
        }

    # HIGH SENSITIVITY + LARGE FILE
    elif file_size_mb > 10:
        return {
            "algorithm": "Hybrid",
            "display_algorithm": "Hybrid AES-256-GCM + RSA-OAEP",
            "security_level": "High",
            "risk_level": "High",
            "reason": (
                "High sensitivity and large file detected. "
                "Hybrid encryption is selected using AES-256-GCM "
                "for file encryption and RSA-OAEP for key protection."
            )
        }

    # HIGH SENSITIVITY + SMALL/NORMAL FILE
    else:
        return {
            "algorithm": "AES",
            "display_algorithm": "AES-256-GCM",
            "security_level": "High",
            "risk_level": "High",
            "reason": (
                "High sensitivity detected, but the file is below "
                "the hybrid-encryption size threshold. "
                "AES-256-GCM is selected."
            )
        }