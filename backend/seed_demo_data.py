"""
OPTIONAL: fill MongoDB with fake history so you can see the
History and Analytics pages with data.

Run from the backend folder:

    python seed_demo_data.py          # add ~40 demo records
    python seed_demo_data.py --clear  # remove ONLY the demo records

Demo records are tagged  seeded=True, so real records are never touched.
Note: demo files have no key files on disk, so don't try to decrypt them.
"""

import random
import sys
from datetime import datetime, timedelta, timezone

from database.mongodb import (
    encryption_history_collection as enc,
    decryption_history_collection as dec,
)

USER = "demo-user"

if "--clear" in sys.argv:
    a = enc.delete_many({"seeded": True}).deleted_count
    b = dec.delete_many({"seeded": True}).deleted_count
    print(f"Removed {a} encryption and {b} decryption demo records.")
    sys.exit()

random.seed(7)
now = datetime.now(timezone.utc)

ALGOS = [
    ("AES", "AES-256-GCM", "256-bit"),
    ("ChaCha20", "ChaCha20-Poly1305", "256-bit"),
    ("Hybrid", "Hybrid AES-256-GCM + RSA-OAEP", "AES-256 + RSA-2048"),
]
CATS = ["General", "Financial", "Legal", "Medical", "Academic"]
TYPES = ["pdf", "docx", "txt", "png", "jpg"]

for i in range(28):
    ml, name, key = random.choice(ALGOS)
    ext = random.choice(TYPES)
    when = now - timedelta(days=random.random() * 28, hours=random.random() * 5)
    enc.insert_one({
        "seeded": True, "user_id": USER,
        "filename": f"demo_file_{i + 1}.{ext}", "file_type": ext.upper(),
        "file_size_mb": round(random.uniform(0.05, 4), 2),
        "pii_count": random.randint(0, 12),
        "sensitivity_score": random.randint(5, 98),
        "document_category": random.choice(CATS),
        "ml_algorithm": ml, "ml_confidence": round(random.uniform(0.62, 0.98), 3),
        "security_validation": "Approved", "encryption_algorithm": name,
        "key_size": key, "processing_time_ms": round(random.uniform(2, 120), 2),
        "status": "Success", "created_at": when,
    })

for i in range(12):
    _, name, key = random.choice(ALGOS)
    when = now - timedelta(days=random.random() * 28)
    dec.insert_one({
        "seeded": True, "user_id": USER,
        "filename": f"demo_file_{random.randint(1, 28)}.pdf",
        "algorithm": name, "key_type": "256-bit symmetric key",
        "processing_time_ms": round(random.uniform(1, 60), 2),
        "status": "Success", "created_at": when,
    })

print("Added 28 encryption + 12 decryption demo records.")
