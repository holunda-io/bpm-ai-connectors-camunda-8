from langchain import Cohere
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from langchain.llms import AlephAlpha

OPENAI_3_5_WITH_FUNCTIONS = "gpt-3.5-turbo-0613"
OPENAI_4_WITH_FUNCTIONS = "gpt-4-0613"
DEFAULT_OPENAI_MODEL = OPENAI_3_5_WITH_FUNCTIONS

LUMINOUS_SUPREME_CONTROL = "luminous-supreme-control"
COHERE_COMMAND_XLARGE = "command-xlarge-beta"


def get_openai_chat_llm(model_name: str = DEFAULT_OPENAI_MODEL) -> ChatOpenAI:
    return ChatOpenAI(
        model_name=model_name,
        temperature=0,
    )


def supports_openai_functions(llm: BaseLanguageModel):
    return isinstance(llm, ChatOpenAI)


def model_id_to_llm(model_id: str) -> BaseLanguageModel:
    match model_id:
        case "gpt-3.5-turbo":
            return get_openai_chat_llm(model_name=OPENAI_3_5_WITH_FUNCTIONS)
        case "gpt-4":
            return get_openai_chat_llm(model_name=OPENAI_4_WITH_FUNCTIONS)
        case "luminous-supreme":
            return AlephAlpha(model=LUMINOUS_SUPREME_CONTROL)
        case "cohere-command-xlarge":
            return Cohere(model=COHERE_COMMAND_XLARGE, temperature=0.0)


def llm_to_model_tag(llm: BaseLanguageModel) -> str:
    match llm:
        case ChatOpenAI():
            return "openai-chat"
        case AlephAlpha():
            return "aleph-alpha"
        case Cohere():
            return "cohere"
