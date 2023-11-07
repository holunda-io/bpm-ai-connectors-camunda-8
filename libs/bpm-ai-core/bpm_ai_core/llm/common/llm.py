from abc import abstractmethod, ABC
from typing import List, Optional, Dict, Any, Type

from langsmith import traceable
from openai.types.chat import ChatCompletionMessageParam
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from bpm_ai_core.llm.common.message import ChatMessage
from bpm_ai_core.llm.common.function import Function
from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.tracing.tracing import LangsmithTracer, LangsmithTracer


class LLM(ABC):
    """
    Abstract class for large language models.
    """

    model: str
    temperature: float = 0.0
    max_retries: int = 5
    retryable_exceptions: List[Type[BaseException]] = [Exception]

    tracer = LangsmithTracer()

    @retry(
        wait=wait_exponential(multiplier=1.5, min=2, max=60),
        stop=stop_after_attempt(max_retries),
        retry=retry_if_exception_type(*retryable_exceptions)
    )
    def predict(
        self,
        prompt: Prompt,
        output_schema: Optional[Dict[str, Any]] = None,
        functions: Optional[List[Function]] = None
    ) -> ChatMessage:
        if output_schema and functions:
            raise ValueError("Must not pass both an output_schema and functions")

        messages = prompt.format(llm_name=self.name())

        self.tracer.start_llm_trace(self, messages, self.predict.retry.statistics['attempt_number'], functions)
        completion = self._predict(messages, output_schema, functions)
        self.tracer.end_llm_trace(completion)

        return completion

    @abstractmethod
    def _predict(
        self,
        messages: List[ChatMessage],
        output_schema: Optional[Dict[str, Any]] = None,
        functions: Optional[List[Function]] = None
    ) -> ChatMessage:
        pass

    @abstractmethod
    def name(self) -> str:
        pass
