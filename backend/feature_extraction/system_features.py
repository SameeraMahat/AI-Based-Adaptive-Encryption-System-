
import os
import mimetypes
import psutil


def extract_system_features(file_path):
    """
    Extract file metadata and current system resource usage.
    Preserve exact file size in bytes for policy decisions.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()

    mime_type, _ = mimetypes.guess_type(file_path)

    # Keep full precision for ML input; policy should use exact bytes.
    file_size_mb = file_size / (1024 * 1024)

    # Runtime system information
    cpu_usage = round(psutil.cpu_percent(interval=0.1), 2)
    ram_usage = round(psutil.virtual_memory().percent, 2)

    file_type = file_extension.lstrip(".").upper()

    return {
        "file_name": file_name,
        "file_extension": file_extension,
        "file_type": file_type,
        "file_size_bytes": file_size,
        "file_size_mb": file_size_mb,
        "mime_type": mime_type,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
    }
