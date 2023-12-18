import os
import base64
from typing import Sequence, List, Optional, Tuple, Iterator

from langchain.load.serializable import Serializable
from langchain.schema import BaseStore


class FileStore(BaseStore[str, str]):

    def __init__(self, directory: str) -> None:
        """Initialize the file-based store with a specified directory."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.directory = directory

    def _key_to_filepath(self, key: str) -> str:
        """Convert a key to its corresponding file path using Base64 encoding."""
        encoded_key = base64.urlsafe_b64encode(key.encode()).decode()
        return os.path.join(self.directory, encoded_key)

    def _filepath_to_key(self, filepath: str) -> str:
        """Convert a Base64 encoded filepath back to its original key."""
        encoded_key = os.path.basename(filepath)
        return base64.urlsafe_b64decode(encoded_key.encode()).decode()

    def mget(self, keys: Sequence[str]) -> List[Optional[str]]:
        """Get the values associated with the given keys."""
        values = []
        for key in keys:
            filepath = self._key_to_filepath(key)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    values.append(f.read())
            else:
                values.append(None)
        return values

    def mset(self, key_value_pairs: Sequence[Tuple[str, str]]) -> None:
        """Set the values for the given keys."""
        for key, value in key_value_pairs:
            filepath = self._key_to_filepath(key)
            with open(filepath, 'w') as f:
                f.write(value)

    def mdelete(self, keys: Sequence[str]) -> None:
        """Delete the given keys and their associated values."""
        for key in keys:
            filepath = self._key_to_filepath(key)
            if os.path.exists(filepath):
                os.remove(filepath)

    def yield_keys(self, prefix: Optional[str] = None) -> Iterator[str]:
        """Get an iterator over keys that match the given prefix."""
        for filename in os.listdir(self.directory):
            decoded_key = self._filepath_to_key(filename)
            if prefix is None or decoded_key.startswith(prefix):
                yield decoded_key
