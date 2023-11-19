import os
from typing import List
from urllib.parse import urlparse


def is_supported_file(url_or_path: str, supported_extensions: List[str]) -> bool:
    url_or_path = url_or_path.strip()
    # Normalize the extensions to lowercase
    supported_extensions = [ext.lower() for ext in supported_extensions]

    # Extract the path from URL if it's a URL
    parsed_url = urlparse(url_or_path)
    path = parsed_url.path if parsed_url.scheme else url_or_path

    # Remove trailing slash if present
    if path.endswith('/'):
        path = path[:-1]

    # Extract the file extension
    _, file_extension = os.path.splitext(path)
    file_extension = file_extension.lower().lstrip('.')

    # Check if the file extension is in the list of supported extensions
    return file_extension in supported_extensions