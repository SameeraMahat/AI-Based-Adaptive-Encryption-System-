from flask import Flask, render_template, request
import os

from feature_extractor.file_features import get_file_features
from feature_extractor.system_features import get_system_features
from feature_extractor.pii_detector import extract_text, detect_pii
from feature_extractor.sensitivity import calculate_sensitivity

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return "No file selected."

    file = request.files["file"]

    if file.filename == "":
        return "No file selected."

    # Save uploaded file
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Extract file features
    features = get_file_features(filepath)

    # Extract system features
    system_features = get_system_features()

    # Read file content
    text = extract_text(filepath)

    # Detect PII
    pii = detect_pii(text)

    sensitivity = calculate_sensitivity(pii)

    # Render result page
    return render_template(
        "result.html",
        features=features,
        system=system_features,
        pii=pii,
        sensitivity=sensitivity
    )


if __name__ == "__main__":
    app.run(debug=True)