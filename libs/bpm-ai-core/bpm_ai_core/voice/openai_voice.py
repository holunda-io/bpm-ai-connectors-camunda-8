import io
import time
from typing import Optional, Dict, Any, Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play, _play_with_ffplay, _play_with_simpleaudio
import speech_recognition as sr
from bpm_ai_core.voice.common.voice import Voice


class OpenAIVoice(Voice):
    """
    `OpenAI` TTS and STT API.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.
    """

    def __init__(
        self,
        whisper_model: str = "whisper-1",
        voice_model: str = "tts-1",
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy",
        client_kwargs: Optional[Dict[str, Any]] = None
    ):
        self.whisper_model = whisper_model
        self.voice_model = voice_model
        self.voice = voice
        self.recognizer = sr.Recognizer()
        self.client = OpenAI(
            **(client_kwargs or {})
        )

    def speak(self, text: str):
        response = self.client.audio.speech.create(
            model=self.voice_model,
            voice=self.voice,
            input=text
        )
        #response.stream_to_file("speech.mp3")
        # Convert the binary response content to a byte stream
        byte_stream = io.BytesIO(response.content)
        # Read the audio data from the byte stream
        audio = AudioSegment.from_file(byte_stream, format="mp3", codec="mp3")
        #play(audio) # todo segfault
        _play_with_ffplay(audio)

    def listen(self, language: Optional[str] = None) -> str:
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
            print("[listen] Processing...")
            wav_bytes = io.BytesIO(audio.get_wav_data())
            wav_bytes.name = "f.wav"
            transcript = self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=wav_bytes,
                response_format="text",
                **{"language": language}
            )
            return transcript
