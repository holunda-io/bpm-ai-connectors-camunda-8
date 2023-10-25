import json
from typing import Dict, Any, Optional, List, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from typing_extensions import TypedDict, Literal

from bpm_ai_core.llm.common.tool import Tool


class ChatOpenAI:
    """
    `OpenAI` Chat large language models API.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.
    """

    model: str
    """Model name to use."""
    temperature: float
    """What sampling temperature to use."""

    client: OpenAI

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        max_retries: int = 3,
        client_kwargs: Optional[Dict[str, Any]] = None
    ):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(
            max_retries=max_retries,
            **(client_kwargs or {})
        )

    def predict_text(self, user_message: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": user_message}]
        )
        return completion.choices[0].message.content

    def predict_message(
        self,
        messages: List[ChatCompletionMessageParam],
    ) -> ChatCompletionMessage:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages
        )
        return completion.choices[0].message

    def predict_json(
        self,
        messages: List[ChatCompletionMessageParam],
        output_schema: Dict[str, Any],
    ) -> dict:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
            function_call={"name": "store_result"},
            functions=[
                {
                    "name": "store_result",
                    "description": "Stores your result",
                    "parameters": {
                        "type": "object",
                        "properties": output_schema,
                        "required": list(output_schema.keys()),
                    }
                }
            ]
        )
        assistant_message = completion.choices[0].message
        if assistant_message.function_call:
            try:
                json_object = json.loads(assistant_message.function_call.arguments)
                return json_object
            except ValueError as e:
                print(e)
                return {}
        else:
            print("WARNING: No function call!")
            return {}
