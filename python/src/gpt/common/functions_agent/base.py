"""Module implements an agent that uses OpenAI's APIs function enabled API."""
from typing import Any, List, Optional, Sequence, Tuple, Union

from langchain.agents import BaseSingleActionAgent, AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent, _format_intermediate_steps, _parse_ai_message
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import Callbacks
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    BaseMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder, SystemMessagePromptTemplate,
)
from langchain.schema import (
    AgentAction,
    AgentFinish,
    BaseMessage,
)
from langchain.tools import BaseTool


class FunctionsAgent(OpenAIFunctionsAgent):
    """An Agent driven by OpenAIs function powered API. Customized variant of OpenAIFunctionsAgent"""

    output_key: str = "output"

    @property
    def return_values(self) -> List[str]:
        """Return values of the agent."""
        return [self.output_key]

    @property
    def input_keys(self) -> List[str]:
        """The input keys."""
        return list(set(self.prompt.input_variables) - {"agent_scratchpad"})

    @classmethod
    def create_prompt(
        cls,
        system_message_template: Optional[str] = None,
        human_message_template: Optional[str] = None,
    ) -> BasePromptTemplate:
        messages: List[Union[BaseMessagePromptTemplate, BaseMessage]]
        if system_message_template:
            messages = [SystemMessagePromptTemplate.from_template(system_message_template)]
        else:
            messages = []

        messages.extend(
            [
                HumanMessagePromptTemplate.from_template(human_message_template),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        return ChatPromptTemplate.from_messages(messages=messages)

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """Given input, decided what to do.
        Args:
            intermediate_steps: Steps the LLM has taken to date, along with observations
            **kwargs: User inputs.
        Returns:
            Action specifying what tool to use.
        """
        # user_input = kwargs["input"]
        agent_scratchpad = _format_intermediate_steps(intermediate_steps)
        prompt = self.prompt.format_prompt(
            **kwargs, agent_scratchpad=agent_scratchpad
        )
        messages = prompt.to_messages()
        predicted_message = self.llm.predict_messages(
            messages, functions=self.functions, callbacks=callbacks
        )
        agent_decision = _parse_ai_message(predicted_message)
        if isinstance(agent_decision, AgentFinish):
            agent_decision = AgentFinish(  # todo hack to avoid copying _parse_ai_message here just to have a configurable output key
                return_values={self.output_key: agent_decision.return_values["output"]},
                log=agent_decision.log
            )
        return agent_decision

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        system_message: str = "You are a helpful AI assistant.",
        human_message: str = "{input}",
        output_key: str = "output",
        callback_manager: Optional[BaseCallbackManager] = None,
        **kwargs: Any,
    ) -> BaseSingleActionAgent:
        """Construct an agent from an LLM and tools."""
        if not isinstance(llm, ChatOpenAI):
            raise ValueError("Only supported with OpenAI models.")
        prompt = cls.create_prompt(
            system_message_template=system_message,
            human_message_template=human_message,
        )
        return cls(
            llm=llm,
            prompt=prompt,
            tools=tools,
            callback_manager=callback_manager,
            output_key=output_key,
            **kwargs,
        )
