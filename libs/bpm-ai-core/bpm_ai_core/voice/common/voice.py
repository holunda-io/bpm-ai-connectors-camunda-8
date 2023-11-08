from abc import ABC, abstractmethod


class Voice(ABC):

    @abstractmethod
    def speak(self, text: str):
        pass
