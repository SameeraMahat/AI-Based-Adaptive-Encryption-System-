import os
import pdfplumber
import docx
import easyocr


def extract_pdf(file_path):
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_docx(file_path):
    document = docx.Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()


def extract_image(file_path):
    # Create the OCR reader only when an image is processed
    reader = easyocr.Reader(['en'], gpu=False)

    results = reader.readtext(file_path)

    text = ""

    for result in results:
        text += result[1] + " "

    return text


def extract_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_pdf(file_path)

    elif extension == ".docx":
        return extract_docx(file_path)

    elif extension == ".txt":
        return extract_txt(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:
        return extract_image(file_path)

    else:
        raise ValueError("Unsupported file format")