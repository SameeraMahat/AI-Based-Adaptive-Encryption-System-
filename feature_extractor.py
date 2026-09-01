"""
Extracts the same features our classifier was trained on, but from a REAL
uploaded file instead of typed-in test data.

Mirrors the keyword banks used in data/generate_dataset.py so real files
get scored using the same vocabulary the model learned.
"""

# Same keyword banks as data/generate_dataset.py (kept in sync manually for now;
# a future improvement could load these from one shared config file).
ALL_KEYWORDS = {
    "roll_no", "date", "subject", "timetable", "notice", "attendance", "class",
    "holiday_list", "room_no", "period", "syllabus", "event_name",
    "employee_id", "rating", "comments", "feedback", "department", "designation",
    "project_name", "manager_name", "shift_timing", "leave_balance",
    "salary", "bank_acc", "pan_no", "tax", "bonus", "ifsc_code",
    "loan_amount", "credit_score", "investment", "ctc",
    "diagnosis", "medication", "aadhar_no", "blood_group", "patient_id", "allergy",
    "passport_no", "biometric_id", "insurance_no", "surgery_history",
}

TEXT_LIKE_EXTENSIONS = {"csv", "txt", "docx", "xlsx", "pdf", "json"}


def get_file_type(filename: str) -> str:
    """Extracts the extension from a filename (lowercase, no dot)."""
    if "." not in filename:
        return "unknown"
    return filename.rsplit(".", 1)[-1].lower()


def get_size_kb(file_bytes: bytes) -> float:
    """Real file size in KB, rounded to 1 decimal."""
    return round(len(file_bytes) / 1024, 1)


def scan_keywords(file_bytes: bytes, file_type: str) -> tuple:
    """
    Scans the file's raw content for any of our known sensitive keywords.

    For text-like files (csv, txt, docx, xlsx, pdf, json), we attempt to
    decode the bytes as text and search for keyword matches.

    For binary/media files (images, video), we can't meaningfully search
    content this way -- keyword scanning is skipped and sensitivity for
    these files leans more on file_type + size (a known limitation, noted
    in the project report).

    Returns: (keywords_present_string, keyword_count)
    """
    if file_type not in TEXT_LIKE_EXTENSIONS:
        return "", 0

    try:
        text = file_bytes.decode("utf-8", errors="ignore").lower()
    except Exception:
        return "", 0

    found = sorted({kw for kw in ALL_KEYWORDS if kw in text})

    keywords_present = ";".join(found) if found else "none"
    keyword_count = len(found)

    return keywords_present, keyword_count


def extract_features(filename: str, file_bytes: bytes) -> dict:
    """
    Full feature extraction pipeline for one uploaded file.
    Returns a dict matching the format classify_file() expects.
    """
    file_type = get_file_type(filename)
    size_kb = get_size_kb(file_bytes)
    keywords_present, keyword_count = scan_keywords(file_bytes, file_type)

    return {
        "file_type": file_type,
        "size_kb": size_kb,
        "keywords_present": keywords_present,
        "keyword_count": keyword_count,
    }


if __name__ == "__main__":
    # Quick self-test with a fake in-memory "uploaded" file
    sample_bytes = b"salary_sheet content: salary=75000, bank_acc=XXXX1234, pan_no=ABCDE1234F"
    features = extract_features("salary_sheet.csv", sample_bytes)
    print("Extracted features:", features)

    sample_bytes_2 = b"attendance sheet: roll_no 12, date 2026-08-09, subject Maths"
    features_2 = extract_features("attendance.txt", sample_bytes_2)
    print("Extracted features:", features_2)
