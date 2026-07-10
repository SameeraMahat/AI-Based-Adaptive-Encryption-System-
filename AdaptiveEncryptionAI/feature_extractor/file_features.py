import os
import mimetypes
from datetime import datetime


def get_file_features(filepath):

    file_name = os.path.basename(filepath)

    extension = os.path.splitext(filepath)[1].lower()

    size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)

    mime_type = mimetypes.guess_type(filepath)[0]

    created = datetime.fromtimestamp(
        os.path.getctime(filepath)
    ).strftime("%d-%m-%Y %H:%M:%S")

    modified = datetime.fromtimestamp(
        os.path.getmtime(filepath)
    ).strftime("%d-%m-%Y %H:%M:%S")

    return {
        "File Name": file_name,
        "Extension": extension,
        "Size (MB)": size_mb,
        "MIME Type": mime_type,
        "Created": created,
        "Modified": modified
    }