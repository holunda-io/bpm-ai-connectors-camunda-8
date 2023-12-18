from typing import List, Optional, Any, Mapping

from langchain.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain.llms.base import LLM


class FakeLLM(LLM):
    """Fake LLM for testing purposes."""

    responses: List[str]
    response_idx: int = 0

    requests: List[str] = []

    def assert_last_request_contains(self, text: str):
        assert text in self.requests[-1]

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        self.requests += [prompt]

        response = self.responses[self.response_idx]
        self.response_idx += 1

        return response

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        raise Exception()

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "fake-list"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"responses": self.responses}
