import io
from typing import Optional, Dict, Any, Union

from openai import OpenAI

from bpm_ai_core.speech.common.speech import Speech
from bpm_ai_core.util.audio import load_audio


class OpenAISpeech(Speech):
    """
    `OpenAI` STT API.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.
    """

    def __init__(
        self,
        whisper_model: str = "whisper-1",
        client_kwargs: Optional[Dict[str, Any]] = None
    ):
        self.whisper_model = whisper_model
        self.client = OpenAI(
            **(client_kwargs or {})
        )

    def transcribe(self, audio: Union[str, io.BytesIO], language: Optional[str] = None) -> str:
        if isinstance(audio, str):
            audio = load_audio(audio)
        transcript = self.client.audio.transcriptions.create(
            model=self.whisper_model,
            file=audio,
            **{"language": language} if language else {}
        )
        print(transcript)
        return transcript.text
