"""Fake LLM wrapper for testing purposes."""
from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM


class FakeLLM(LLM):
    """Fake LLM wrapper for testing purposes."""

    def noop(self, x):
        return x

    f = noop

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "fake"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        return self.f(prompt)

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"lambda": self.f}
