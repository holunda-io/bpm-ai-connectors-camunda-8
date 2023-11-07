import json

from typing import Dict, Any, Optional, List, Union

from langsmith import traceable
from openai import OpenAI, APIConnectionError, InternalServerError, RateLimitError
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from typing_extensions import TypedDict, Literal

from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ChatMessage, FunctionCallMessage
from bpm_ai_core.llm.common.function import Function
from bpm_ai_core.util.openai import messages_to_openai_dicts, json_schema_to_openai_function


class ChatOpenAI(LLM):
    """
    `OpenAI` Chat large language models API.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.
    """

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        max_retries: int = 3,
        client_kwargs: Optional[Dict[str, Any]] = None
    ):
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.retryable_exceptions = [
            RateLimitError, InternalServerError, APIConnectionError
        ]
        self.client = OpenAI(
            max_retries=0,  # we use own retry logic
            **(client_kwargs or {})
        )

    def _predict(
        self,
        messages: List[ChatMessage],
        output_schema: Optional[Dict[str, Any]] = None,
        functions: Optional[List[Function]] = None
    ) -> ChatMessage:
        openai_functions = []
        if output_schema:
            openai_functions = [self._get_default_result_function(output_schema)]
        elif functions:
            openai_functions = [json_schema_to_openai_function(f.name, f.description, f.args_schema) for f in functions]

        completion = self._run_completion(messages, openai_functions)

        message = completion.choices[0].message
        if message.function_call:
            if output_schema:
                return ChatMessage(role=message.role, content=self._load_function_call_json(message))
            else:
                return self._openai_function_call_to_function_message(message, functions)
        else:
            return ChatMessage(role=message.role, content=message.content)

    def _run_completion(self, messages: List[ChatMessage], functions: List[dict]):
        return self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages_to_openai_dicts(messages),
            **({
                   "function_call": {"name": functions[0]["name"]} if (len(functions) == 1) else "auto",
                   "functions": functions
               } if functions else {})
        )

    @staticmethod
    def _openai_function_call_to_function_message(message: ChatCompletionMessage, functions) -> FunctionCallMessage:
        function_name = message.function_call.name
        return FunctionCallMessage(
            name=function_name,
            content=message.content,
            payload=message.function_call.arguments,
            function=next((item for item in functions if item.name == function_name), None)
        )

    @staticmethod
    def _load_function_call_json(message: ChatCompletionMessage):
        try:
            json_object = json.loads(message.function_call.arguments)
        except ValueError as e:
            print(e)
            json_object = None
        return json_object

    @staticmethod
    def _get_default_result_function(output_schema):
        return {
            "name": "store_result",
            "description": "Stores your result",
            "parameters": {
                "type": "object",
                "properties": output_schema,
                "required": list(output_schema.keys()),
            }
        }

    def name(self) -> str:
        return "openai"
