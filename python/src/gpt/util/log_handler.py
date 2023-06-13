import logging
from typing import Dict, Any, List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult


class ChatLogHandler(BaseCallbackHandler):

    def __init__(self, filename: str):
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler(filename)
        formatter = logging.Formatter('%(message)s')  # log raw messages
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        self.logger.info("----------------------\nPrompt\n----------------------")
        for p in prompts:
            self.logger.info(p)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.logger.info("----------------------\nCompletion\n----------------------")
        self.logger.info(response.generations[0][0].text)
