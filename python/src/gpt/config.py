from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI


OPENAI_3_5_WITH_FUNCTIONS = "gpt-3.5-turbo-0613"
OPENAI_4_WITH_FUNCTIONS = "gpt-4-0613"
DEFAULT_OPENAI_MODEL = OPENAI_3_5_WITH_FUNCTIONS


def get_openai_chat_llm(model_name: str = DEFAULT_OPENAI_MODEL) -> ChatOpenAI:
    return ChatOpenAI(
        model_name=model_name,
        temperature=0,
    )


def supports_openai_functions(llm: BaseLanguageModel):
    return isinstance(llm, ChatOpenAI) and llm.model_name.endswith('0613')


def model_id_to_llm(model_id: str) -> BaseLanguageModel:
    match model_id:
        case "gpt-3.5-turbo":
            return get_openai_chat_llm(model_name=OPENAI_3_5_WITH_FUNCTIONS)
        case "gpt-4":
            return get_openai_chat_llm(model_name=OPENAI_4_WITH_FUNCTIONS)
