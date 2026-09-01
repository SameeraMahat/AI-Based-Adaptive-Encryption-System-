"""
FastAPI app for the AI-Based Adaptive Encryption System.

Endpoints:
- POST /encrypt  -> upload a real file, runs the FULL pipeline:
                    classify -> decide algorithm -> encrypt
                    returns sensitivity, chosen algorithm, reason, and
                    confirms decryption works.

Run with:  uvicorn main:app --reload
Then open: http://127.0.0.1:8000/  (a simple upload page)
Or use the interactive API docs: http://127.0.0.1:8000/docs
"""

import os
import joblib
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from feature_extractor import extract_features
from train_classifier import build_features
from decision_engine import DecisionContext, decide_algorithm
from device_stats import get_device_stats
from encrypt_dispatcher import encrypt_file, decrypt_file, generate_ecc_keypair

app = FastAPI(title="AI-Based Adaptive Encryption System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)

# Load the trained classifier + encoders ONCE at startup (not per-request)
model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
file_type_encoder = joblib.load(os.path.join(BASE_DIR, "file_type_encoder.pkl"))
keyword_vectorizer = joblib.load(os.path.join(BASE_DIR, "keyword_vectorizer.pkl"))


def classify(features: dict) -> str:
    row = pd.DataFrame([features])
    X, _, _ = build_features(row, file_type_encoder, keyword_vectorizer, fit=False)
    prediction = model.predict(X)[0]
    return prediction


@app.get("/", response_class=HTMLResponse)
def upload_page():
    """A minimal HTML upload form for manual testing/demo."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI-Based Adaptive Encryption System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }
            h1 { font-size: 22px; }
            #result { margin-top: 25px; padding: 15px; background: #f4f4f4; border-radius: 6px; white-space: pre-wrap; font-family: monospace; }
            select, input, button { padding: 8px; margin: 5px 0; }
            button { cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>AI-Based Adaptive Encryption System</h1>
        <p>Upload a file to see the AI classify its sensitivity and pick an encryption algorithm.</p>

        <form id="uploadForm">
            <div><input type="file" id="fileInput" required></div>
            <div>
                User role:
                <select id="userRole">
                    <option value="employee">Employee</option>
                    <option value="admin">Admin</option>
                    <option value="guest">Guest</option>
                </select>
            </div>
            <div>
                Threat level:
                <select id="threatLevel">
                    <option value="normal">Normal</option>
                    <option value="elevated">Elevated</option>
                    <option value="high">High</option>
                </select>
            </div>
            <button type="submit">Encrypt File</button>
        </form>

        <div id="result"></div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('fileInput');
                const userRole = document.getElementById('userRole').value;
                const threatLevel = document.getElementById('threatLevel').value;
                const resultDiv = document.getElementById('result');

                if (!fileInput.files.length) return;

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('user_role', userRole);
                formData.append('threat_level', threatLevel);

                resultDiv.textContent = 'Processing...';

                try {
                    const response = await fetch('/encrypt', { method: 'POST', body: formData });
                    const data = await response.json();
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    resultDiv.textContent = 'Error: ' + err;
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/encrypt")
async def encrypt_endpoint(
    file: UploadFile = File(...),
    user_role: str = Form("employee"),
    threat_level: str = Form("normal"),
):
    """
    Full pipeline: upload a real file -> classify -> decide -> encrypt -> verify.
    """
    file_bytes = await file.read()

    # STEP 1: Extract real features from the uploaded file
    features = extract_features(file.filename, file_bytes)

    # STEP 2: Classify sensitivity using the trained model
    sensitivity = classify(features)

    # STEP 3: Read real device stats
    stats = get_device_stats()

    # STEP 4: Decision engine picks the algorithm
    ctx = DecisionContext(
        sensitivity=sensitivity,
        file_size_kb=features["size_kb"],
        user_role=user_role,
        cpu_percent=stats["cpu_percent"],
        battery_percent=stats["battery_percent"],
        threat_level=threat_level,
    )
    decision = decide_algorithm(ctx)

    # STEP 5: Actually encrypt (and verify decrypt) the file
    if decision["algorithm"] == "Hybrid":
        receiver_private, receiver_public = generate_ecc_keypair()
        package = encrypt_file(file_bytes, "Hybrid", receiver_public_key=receiver_public)
        decrypted = decrypt_file(package, receiver_private_key=receiver_private)
    else:
        package = encrypt_file(file_bytes, decision["algorithm"])
        decrypted = decrypt_file(package)

    return {
        "filename": file.filename,
        "extracted_features": features,
        "predicted_sensitivity": sensitivity,
        "device_stats": stats,
        "chosen_algorithm": decision["algorithm"],
        "reason": decision["reason"],
        "original_size_bytes": len(file_bytes),
        "encrypted_size_bytes": len(package["ciphertext"]),
        "decryption_verified": decrypted == file_bytes,
    }
