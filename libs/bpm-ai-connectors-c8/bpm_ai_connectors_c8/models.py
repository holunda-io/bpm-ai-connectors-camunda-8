from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.speech.stt.openai_whisper import OpenAIWhisper
from bpm_ai_core.speech.stt.stt import STTModel


def model_id_to_llm(
    model_id: str
) -> LLM:
    if model_id.startswith("gpt"):
        return ChatOpenAI(model=model_id)


def model_id_to_stt(
    model_id: str
) -> STTModel | None:
    if model_id.startswith("openai"):
        return OpenAIWhisper()
    else:
        return None
