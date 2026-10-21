
import re

CATEGORY_KEYWORDS = {
    "Finance": [
        "invoice", "payment", "bank", "tax", "salary",
        "budget", "gst", "balance", "account", "finance"
    ],
    "HR": [
        "employee", "resume", "recruitment", "leave",
        "attendance", "joining", "designation", "hr"
    ],
    "Legal": [
        "agreement", "contract", "law", "court",
        "clause", "legal", "plaintiff", "defendant"
    ],
    "Medical": [
        "patient", "diagnosis", "hospital", "medicine",
        "doctor", "treatment", "prescription"
    ],
    "Research": [
        "research", "experiment", "dataset", "analysis",
        "methodology", "results", "paper", "journal"
    ],
    "Business": [
        "client", "project", "meeting", "proposal",
        "strategy", "company", "business", "roadmap"
    ],
    "Personal": [
        "diary", "personal", "family", "friend",
        "vacation", "birthday"
    ]
}


def classify_document(text):
    """
    Classify a document using whole-word keyword matching.

    Returns:
        {
            "document_category": str,
            "category_confidence": float
        }

    Confidence is the winning category's share of all keyword
    matches. It is a heuristic, not a calibrated probability.
    """

    if not isinstance(text, str) or not text.strip():
        return {
            "document_category": "General",
            "category_confidence": 0.0
        }

    text = text.casefold()
    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        count = 0

        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword.casefold()) + r"\b"
            count += len(re.findall(pattern, text))

        scores[category] = count

    total_matches = sum(scores.values())

    if total_matches == 0:
        return {
            "document_category": "General",
            "category_confidence": 0.0
        }

    # Stable tie-breaking: preserve CATEGORY_KEYWORDS order.
    best_category = max(
        CATEGORY_KEYWORDS,
        key=lambda category: scores[category]
    )

    # If multiple categories tie for the highest score,
    # avoid presenting the result as a confident classification.
    highest_score = scores[best_category]
    tied_categories = [
        category
        for category, score in scores.items()
        if score == highest_score
    ]

    if len(tied_categories) > 1:
        confidence = round(highest_score / total_matches, 2)
    else:
        confidence = round(highest_score / total_matches, 2)

    return {
        "document_category": best_category,
        "category_confidence": confidence
    }
