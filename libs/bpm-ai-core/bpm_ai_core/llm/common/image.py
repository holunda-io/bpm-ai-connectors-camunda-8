import base64
import os
from io import BytesIO

import requests
from PIL import Image


def load_image(path: str) -> Image:
    """
    Load an image from a local path or a web URL into a Pillow Image object.

    Parameters:
    - path (str): A file system path or a URL of an image.

    Returns:
    - Image: A Pillow Image object.
    """
    if path.startswith('http://') or path.startswith('https://'):
        # Handle web URL
        response = requests.get(path)
        image = Image.open(BytesIO(response.content))
    elif os.path.isfile(path):
        # Handle local file path
        image = Image.open(path)
    else:
        raise ValueError("The path provided is neither a valid URL nor a file path.")

    return image


def base64_encode_image(image: Image):
    """
    Get a base64 encoded string from a Pillow Image object.

    Parameters:
    - image (Image): A Pillow Image object.

    Returns:
    - str: Base64 encoded string of the image.
    """
    buffered = BytesIO()
    image.save(buffered, format=image.format or "JPEG")  # Assuming JPEG if format is not provided
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode('utf-8')
