from typing import Dict, Any, Optional, List

from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage, HumanMessage, BaseLanguageModel

from gpt.agents.common.agent.base import Agent, AgentParameterResolver, DEFAULT_OUTPUT_KEY
from gpt.agents.common.agent.output_parser import AgentOutputParser, AgentAction
from gpt.agents.common.agent.react.output_parser import ReActOutputParser
from gpt.agents.common.agent.react.prompt import OBSERVATION_PREFIX, THOUGHT_PREFIX
from gpt.agents.common.agent.step import AgentStep
from gpt.agents.common.agent.toolbox import Toolbox


class ReActParameterResolver(AgentParameterResolver):
    def resolve_parameters(self, inputs: Dict[str, Any], agent: Agent, agent_step: AgentStep, **kwargs) -> Dict[str, Any]:
        """
        A parameter resolver for ReAct-based agents that returns the input, the tool names, the tool names
        with descriptions, and the transcript (internal monologue).
        """
        return {
            "input": inputs["input"],
            "context": inputs["context"],
            "tool_names": agent.toolbox.get_tool_names(),
            "tool_names_with_descriptions": agent.toolbox.get_tool_names_with_descriptions(),
            "transcript": agent_step.transcript,
        }


class ReActAgent(Agent):

    @classmethod
    def create(
        cls,
        llm: BaseChatModel,
        system_prompt_template: Optional[SystemMessagePromptTemplate] = None,
        user_prompt_templates: Optional[List[BaseMessagePromptTemplate]] = None,
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None,
        prompt_parameters_resolver: Optional[AgentParameterResolver] = None,
        output_parser: Optional[AgentOutputParser] = None,
        output_key: str = DEFAULT_OUTPUT_KEY,
        stop_words: Optional[List[str]] = None,
        toolbox: Optional[Toolbox] = None,
        **kwargs
    ):
        return cls(
            llm=llm,
            system_prompt_template=system_prompt_template or SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
            user_prompt_templates=user_prompt_templates or [HumanMessagePromptTemplate.from_template("{input}")],
            few_shot_prompt_messages=few_shot_prompt_messages,
            prompt_parameters_resolver=prompt_parameters_resolver or ReActParameterResolver(),
            output_parser=output_parser or ReActOutputParser(output_key=output_key),
            toolbox=toolbox,
            stop_words=stop_words or [OBSERVATION_PREFIX],
            **kwargs
        )

    @staticmethod
    def _create_observation_message(action: AgentAction, observation: str) -> BaseMessage:
        return HumanMessage(content=f"{OBSERVATION_PREFIX} {observation}\n{THOUGHT_PREFIX}")
