from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.openai_chat import ChatOpenAI


def model_id_to_llm(
    model_id: str
) -> LLM:
    match model_id:
        case "GPT_3":
            return ChatOpenAI(model="gpt-3.5-turbo-1106")
        case "GPT_4":
            return ChatOpenAI(model="gpt-4-1106-preview")