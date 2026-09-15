import os
import mimetypes


def extract_system_features(file_path):
    """
    Extract metadata about the uploaded file.
    """

    file_size = os.path.getsize(file_path)

    file_name = os.path.basename(file_path)

    file_extension = os.path.splitext(file_name)[1].lower()

    mime_type, _ = mimetypes.guess_type(file_path)

    features = {
        "file_name": file_name,
        "file_extension": file_extension,
        "file_size_bytes": file_size,
        "mime_type": mime_type
    }

    return features