"""Fake LLM wrapper for testing purposes."""
from typing import Any, List, Mapping, Optional, Dict

from langchain.callbacks.manager import CallbackManagerForLLMRun, Callbacks, AsyncCallbackManagerForLLMRun
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import SimpleChatModel, BaseChatModel
from langchain.llms.base import LLM
from langchain.schema import BaseMessage, ChatResult, ChatGeneration, LLMResult

from util.prompt import messages_to_str


class FakeChatOpenAI(BaseChatModel):
    """Fake ChatModel for testing purposes."""

    responses: List[BaseMessage]
    response_idx: int = 0

    requests: List[List[BaseMessage]] = []
    functions: List[List[Dict]] = []
    function_calls: List[str] = []

    def assert_last_request_contains(self, text: str):
        assert text in messages_to_str(self.requests[-1])

    def assert_last_request_not_contains(self, text: str):
        assert text not in messages_to_str(self.requests[-1])

    def assert_last_request_defined_function(self, function_name: str, function_call: bool = False):
        assert function_name in [f['name'] for f in self.functions[-1]]
        assert (self.function_calls[-1] == function_name) == function_call

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.requests += [messages]
        self.functions += [kwargs.get("functions", [])]
        self.function_calls += [kwargs.get("function_call", {'name': None})['name']]

        response = self.responses[self.response_idx]
        self.response_idx += 1

        gen = ChatGeneration(
            message=response,
        )
        return ChatResult(generations=[gen], llm_output={})

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        raise NotImplementedError()

    @property
    def _llm_type(self) -> str:
        return "fake-list-openai-chat-model"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"responses": self.responses}


