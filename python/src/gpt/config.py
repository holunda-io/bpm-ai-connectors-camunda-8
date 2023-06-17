from langchain.chat_models import ChatOpenAI
from gpt.util.log_handler import ChatLogHandler

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"


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
