from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from gpt.util.log_handler import ChatLogHandler

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo-0613"


def get_default_llm():
    return get_chat_llm()


def get_chat_llm(model_name: str = DEFAULT_OPENAI_MODEL):
    return ChatOpenAI(
        model_name=model_name,
        temperature=0,
        callbacks=[
            ChatLogHandler('chatlog.txt')
        ]
    )


def supports_openai_functions(llm: BaseLanguageModel):
    return isinstance(llm, ChatOpenAI) and llm.model_name.endswith('0613')
