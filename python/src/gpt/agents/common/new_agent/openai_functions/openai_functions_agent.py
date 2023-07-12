import re
from typing import Dict, Any, Callable, Optional, List

from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate
from langchain.schema import AIMessage, BaseMessage, FunctionMessage, AgentAction
from langchain.tools import format_tool_to_openai_function

from gpt.agents.common.new_agent.base import Agent, AgentParameterResolver
from gpt.agents.common.new_agent.openai_functions.output_parser import OpenAIFunctionsOutputParser
from gpt.agents.common.new_agent.output_parser import AgentOutputParser
from gpt.agents.common.new_agent.step import AgentStep
from gpt.agents.common.new_agent.toolbox import Toolbox


class OpenAIFunctionsParameterResolver(AgentParameterResolver):
    def resolve_parameters(self, inputs: Dict[str, Any], agent: Agent, agent_step: AgentStep, **kwargs) -> Dict[str, Any]:
        """

        """
        return {
            "input": inputs["input"],
            #"context": inputs["context"],
            "transcript": agent_step.transcript,
        }


class OpenAIFunctionsAgent(Agent):

    def __init__(
        self,
        llm: ChatOpenAI,
        system_prompt_template: Optional[SystemMessagePromptTemplate] = None,
        user_prompt_template: Optional[HumanMessagePromptTemplate] = None,
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None,
        prompt_parameters_resolver: Optional[AgentParameterResolver] = None,
        output_parser: Optional[AgentOutputParser] = None,
        toolbox: Optional[Toolbox] = None,
        stop_words: Optional[List[str]] = None,
        max_steps: int = 10
    ):
        super().__init__(
            llm=llm,
            prompt_template=Agent.create_prompt(
                system_prompt_template or SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
                user_prompt_template or HumanMessagePromptTemplate.from_template("{input}"),
                few_shot_prompt_messages
            ),
            few_shot_prompt_messages=few_shot_prompt_messages,
            prompt_parameters_resolver=prompt_parameters_resolver or OpenAIFunctionsParameterResolver(),
            output_parser=output_parser or OpenAIFunctionsOutputParser(),
            toolbox=toolbox,
            stop_words=stop_words,
            max_steps=max_steps
        )

    @property
    def openai_functions(self) -> List[dict]:
        return [dict(format_tool_to_openai_function(t)) for t in self.toolbox.get_tools()]

    def _predict(self, formatted_messages: List[BaseMessage], callbacks: Callbacks = None):
        return self.llm.predict_messages(
            messages=formatted_messages,
            functions=self.openai_functions,
            stop=self.stop_words,
            callbacks=callbacks
        )

    @staticmethod
    def _create_observation_message(action: AgentAction, observation: str) -> BaseMessage:
        return FunctionMessage(name=action.tool, content=observation)

