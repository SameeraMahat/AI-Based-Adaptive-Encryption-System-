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
    Classifies the document into a category based on keyword matching.
    Returns:
    {
        "document_category": "...",
        "category_confidence": 0.xx
    }
    """

    text = text.lower()

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        count = 0

        for keyword in keywords:
            count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))

        scores[category] = count

    total_matches = sum(scores.values())

    if total_matches == 0:
        return {
            "document_category": "General",
            "category_confidence": 0.50
        }

    best_category = max(scores, key=scores.get)

    confidence = round(scores[best_category] / total_matches, 2)

    return {
        "document_category": best_category,
        "category_confidence": confidence
    }