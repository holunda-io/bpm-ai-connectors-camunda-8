import io
from abc import ABC, abstractmethod
from typing import Optional, Union


class Voice(ABC):

    @abstractmethod
    def speak(self, text: str, voice: Optional[str] = None) -> io.BytesIO:
        pass

    @abstractmethod
    def transcribe(self, audio: Union[str, io.BytesIO], language: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def listen(self, language: Optional[str] = None) -> str:
        pass
