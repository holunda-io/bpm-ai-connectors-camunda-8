import re
from typing import Dict, Any, Callable, Optional, List

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, BaseMessage, HumanMessage

from gpt.agents.common.new_agent.base import Agent, AgentParameterResolver
from gpt.agents.common.new_agent.output_parser import AgentOutputParser, AgentAction
from gpt.agents.common.new_agent.react.output_parser import ReActOutputParser
from gpt.agents.common.new_agent.react.prompt import OBSERVATION_PREFIX, THOUGHT_PREFIX
from gpt.agents.common.new_agent.step import AgentStep
from gpt.agents.common.new_agent.toolbox import Toolbox


class ReActParameterResolver(AgentParameterResolver):
    def resolve_parameters(self, inputs: Dict[str, Any], agent: Agent, agent_step: AgentStep, **kwargs) -> Dict[str, Any]:
        """
        A parameter resolver for ReAct-based agents that returns the input, the tool names, the tool names
        with descriptions, and the transcript (internal monologue).
        """
        return {
            "input": inputs["input"],
            #"context": inputs["context"],
            "tool_names": agent.toolbox.get_tool_names(),
            "tool_names_with_descriptions": agent.toolbox.get_tool_names_with_descriptions(),
            "transcript": agent_step.transcript,
        }


class ReActAgent(Agent):

    def __init__(
        self,
        llm: ChatOpenAI,
        prompt_template: ChatPromptTemplate,
        prompt_parameters_resolver: Optional[AgentParameterResolver] = None,
        output_parser: Optional[AgentOutputParser] = None,
        toolbox: Optional[Toolbox] = None,
        stop_words: Optional[List[str]] = None,
        max_steps: int = 10
    ):
        super().__init__(
            llm=llm,
            prompt_template=prompt_template,
            prompt_parameters_resolver=prompt_parameters_resolver or ReActParameterResolver(),
            output_parser=output_parser or ReActOutputParser(),
            toolbox=toolbox,
            stop_words=stop_words or [OBSERVATION_PREFIX],
            max_steps=max_steps
        )

    @staticmethod
    def _create_observation_message(action: AgentAction, observation: str) -> BaseMessage:
        return HumanMessage(content=f"{OBSERVATION_PREFIX} {observation}\n{THOUGHT_PREFIX}")
