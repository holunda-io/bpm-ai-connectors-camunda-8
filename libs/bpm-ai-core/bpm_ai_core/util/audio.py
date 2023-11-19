import io
import os

import requests

from bpm_ai_core.util.file import is_supported_file

supported_audio_extensions = [
   "flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav2", "webm"
]


def is_supported_audio_file(url_or_path: str) -> bool:
    return is_supported_file(url_or_path, supported_extensions=supported_audio_extensions)


def load_audio(path: str) -> io.BytesIO:
    """
    Load an audio file from a local path or a web URL into a BytesIO object.

    Parameters:
    - path (str): A file system path or a URL of an audio file.

    Returns:
    - BytesIO: A BytesIO object containing the audio data.
    """
    if path.startswith('http://') or path.startswith('https://'):
        # Handle web URL
        response = requests.get(path)
        audio = io.BytesIO(response.content)
    elif os.path.isfile(path):
        # Handle local file path
        with open(path, 'rb') as f:
            audio = io.BytesIO(f.read())
            audio.name = f.name
    else:
        raise ValueError("The path provided is neither a valid URL nor a file path.")

    return audio
