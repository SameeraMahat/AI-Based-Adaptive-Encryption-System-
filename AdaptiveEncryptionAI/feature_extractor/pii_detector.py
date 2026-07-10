import re
import os
from PyPDF2 import PdfReader
from docx import Document


def extract_text(filepath):

    extension = os.path.splitext(filepath)[1].lower()

    text = ""

    if extension == ".txt":

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    elif extension == ".pdf":

        reader = PdfReader(filepath)

        for page in reader.pages:
            text += page.extract_text() or ""

    elif extension == ".docx":

        doc = Document(filepath)

        for para in doc.paragraphs:
            text += para.text + "\n"

    return text
def detect_pii(text):

    results = {}

    email = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone = re.findall(
        r"\b\d{10}\b",
        text
    )

    aadhaar = re.findall(
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        text
    )

    pan = re.findall(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        text
    )

    results["Emails"] = email
    results["Phone Numbers"] = phone
    results["Aadhaar"] = aadhaar
    results["PAN"] = pan

    return results