from langchain.chat_models import ChatOpenAI
from gpt.util.log_handler import ChatLogHandler

DEFAULT_OPENAI_MODEL = "gpt-4"


def get_default_llm():
    return ChatOpenAI(
        model_name=DEFAULT_OPENAI_MODEL,
        temperature=0,
        callbacks=[
            ChatLogHandler('chatlog.txt')
        ]
    )


def get_chat_llm(model_name: str = DEFAULT_OPENAI_MODEL):
    return ChatOpenAI(
        model_name=model_name,
        temperature=0,
        callbacks=[
            ChatLogHandler('chatlog.txt')
        ]
    )
