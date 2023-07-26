from __future__ import annotations

import logging
from abc import abstractmethod
from typing import List, Optional, Dict, Any

from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.load.serializable import Serializable
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage
from langchain.tools import BaseTool
from pydantic import Field

from gpt.agents.common.agent.memory import AgentMemory
from gpt.agents.common.agent.output_parser import AgentOutputParser, AgentAction
from gpt.agents.common.agent.step import AgentStep
from gpt.agents.common.agent.toolbox import Toolbox, AutoFinishTool

logger = logging.getLogger(__name__)


class Agent(Chain):
    """
    An Agent answers queries using the tools you give to it. The Agent uses a large
    language model (LLM) through the LLM you initialize it with. To answer a query, the Agent follows this
    sequence:

    1. It generates a thought based on the query.
    2. It decides which tool to use.
    3. It generates the input for the tool.
    4. Based on the output it gets from the tool, the Agent can either stop if it now knows the answer or repeat the
    process of 1) generate thought, 2) choose tool, 3) generate input.
    """

    llm: ChatOpenAI
    prompt_parameters_resolver: AgentParameterResolver
    output_parser: AgentOutputParser
    toolbox: Toolbox = Toolbox()

    user_prompt_templates: List[BaseMessagePromptTemplate]
    prompt_template: ChatPromptTemplate

    stop_words: Optional[List[str]] = None
    max_steps: int = 25
    output_key: str = "output"

    return_last_step = False

    agent_memory: Optional[AgentMemory] = None

    verbose = True

    template_params: Dict[str, Any] = Field({})
    """Contains the resolved template parameters for the current step."""

    @classmethod
    def init(
        cls,
        llm: ChatOpenAI,
        prompt_parameters_resolver: AgentParameterResolver,
        output_parser: AgentOutputParser,
        toolbox: Toolbox,
        system_prompt_template: Optional[SystemMessagePromptTemplate] = None,
        user_prompt_templates: Optional[List[BaseMessagePromptTemplate]] = None,
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None,
        output_key: str = "output",
        stop_words: Optional[List[str]] = None,
        max_steps: int = 25,
        agent_memory: Optional[AgentMemory] = None
    ):
        system_prompt_template = system_prompt_template or SystemMessagePromptTemplate.from_template("You are a helpful assistant.")
        user_prompt_templates = user_prompt_templates or [HumanMessagePromptTemplate.from_template("{input}")]
        return cls(
            llm=llm,
            user_prompt_templates=user_prompt_templates,
            prompt_template=Agent.create_prompt(
                system_prompt_template,
                user_prompt_templates,
                few_shot_prompt_messages
            ),
            prompt_parameters_resolver=prompt_parameters_resolver,
            output_parser=output_parser,
            output_key=output_key,
            toolbox=toolbox,
            stop_words=stop_words,
            max_steps=max_steps,
            agent_memory=agent_memory
        )

    @property
    def input_keys(self) -> List[str]:
        """Return the keys expected to be in the chain input."""
        return ["input", "context"]

    @property
    def output_keys(self) -> List[str]:
        """Return the keys expected to be in the chain output."""
        return [self.output_key] + ("last_step" if self.return_last_step else []) #+ (self.input_keys if self.return_inputs else [])

    def add_tools(self, tools: List[BaseTool]):
        """
        Add the tools to the Agent.

        :param tools: The tools to add to the Agent.
        """
        for tool in tools:
            self.toolbox.add_tool(tool)

    def add_tool(self, tool: BaseTool):
        """
        Add a tool to the Agent.

        :param tool: The tool to add to the Agent.
        """
        self.toolbox.add_tool(tool)

    def has_tool(self, tool_name: str) -> bool:
        """
        Check whether the Agent has a tool with the name you provide.

        :param tool_name: The name of the tool for which you want to check whether the Agent has it.
        """
        return self.toolbox.has_tool(tool_name)

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """
        Runs the Agent.
        """
        agent_step = AgentStep.empty(self.output_parser, self.max_steps)
        while not agent_step.is_last():
            agent_step = self._step(inputs, agent_step, run_manager)

        if self.agent_memory:
            user_messages = ChatPromptTemplate.from_messages(self.user_prompt_templates).format_messages(**self.template_params)
            self.agent_memory.add_transcript(user_messages + agent_step.transcript)

        return self._return(inputs, self.template_params, last_step=agent_step, run_manager=run_manager)

    def _return(
        self,
        inputs: Dict[str, Any],
        template_params: Dict[str, Any],
        last_step: AgentStep,
        run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Dict[str, Any]:
        return {
            **last_step.return_values,
            #**(inputs if self.return_inputs else {}), # already done by Chain...
            **({"last_step": last_step} if self.return_last_step else {})
        }

    def _step(self, inputs: Dict[str, Any], current_step: AgentStep, run_manager: Optional[CallbackManagerForChainRun] = None):
        # plan next step using the LLM
        llm_response = self._plan(inputs, current_step, run_manager.get_child() if run_manager else None)

        # from the LLM response, create the next step
        next_step = current_step.create_next_step(llm_response)

        # run the tool selected by the LLM
        if not next_step.is_last():
            if run_manager:
                run_manager.on_agent_action(next_step.parsed_action, color="green")

            observation = self.toolbox.run_tool(next_step.parsed_action, run_manager.get_child() if run_manager else None)
            observation_message = self._create_observation_message(next_step.parsed_action, observation)

            tool = self.toolbox.get_tool(next_step.parsed_action.tool)
            if isinstance(tool, AutoFinishTool) and tool.is_finish(observation):
                if isinstance(observation, dict):
                    output = observation
                else:
                    output = {self.output_key: str(observation)}

                next_step.manual_finish(output, observation_message)
            else:
                # update the next step with the observation
                next_step.complete(observation_message)
        else:
            if run_manager:
                run_manager.on_agent_finish(next_step.parsed_action, color="blue")
            # final step
            next_step.complete(None)

        return next_step

    def _plan(self, inputs: Dict[str, Any], current_step: AgentStep, callbacks: Callbacks = None) -> BaseMessage:
        # first resolve prompt template params
        self.template_params = self.prompt_parameters_resolver.resolve_parameters(inputs=inputs, agent=self, agent_step=current_step)

        # load history from memory, if any
        self.template_params = {"history": self.agent_memory.get_transcript() if self.agent_memory else [], **self.template_params}

        # check for template parameters mismatch
        self.check_prompt_template(self.template_params)

        # invoke via LLM
        formatted_messages = self.prompt_template.format_messages(**self.template_params)
        return self._predict(formatted_messages, callbacks)

    def _predict(self, formatted_messages: List[BaseMessage], callbacks: Callbacks = None):
        return self.llm.predict_messages(messages=formatted_messages, stop=self.stop_words, callbacks=callbacks)

    @staticmethod
    def _create_observation_message(action: AgentAction, observation: str) -> BaseMessage:
        return HumanMessage(content=observation)

    def check_prompt_template(self, template_params: Dict[str, Any]) -> None:
        """
        Verifies that the Agent's prompt template is adequately populated with the correct parameters
        provided by the prompt parameter resolver.

        :param template_params: The parameters provided by the prompt parameter resolver.
        """
        unused_params = set(template_params.keys()) - set(self.prompt_template.input_variables)

        if "transcript" in unused_params:
            logger.warning(
                "The 'transcript' parameter is missing from the Agent's prompt template. All ReAct agents "
                "that go through multiple steps to reach a goal require this parameter. Please append {transcript} "
                "to the end of the Agent's prompt template to ensure its proper functioning. A temporary prompt "
                "template with {transcript} appended will be used for this run."
            )
            # new_prompt_text = self.prompt_template.prompt_text + "\n {transcript}"
            # self.prompt_template = PromptTemplate(prompt=new_prompt_text)

        elif unused_params:
            logger.debug(
                "The Agent's prompt template does not utilize the following parameters provided by the "
                "prompt parameter resolver: %s. Note that these parameters are available for use if needed.",
                list(unused_params),
            )

    @classmethod
    def create_prompt(
        cls,
        system_prompt_template: SystemMessagePromptTemplate,
        user_prompt_templates: List[BaseMessagePromptTemplate],
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None
    ):
        return ChatPromptTemplate.from_messages([
            system_prompt_template,
            *(few_shot_prompt_messages or []),
            MessagesPlaceholder(variable_name="history"),
            *user_prompt_templates,
            MessagesPlaceholder(variable_name="transcript"),
        ])


class AgentParameterResolver(Serializable):
    """
    A parameter resolver for an agent resolves a dict of prompt input variable values for the current step.
    """

    @abstractmethod
    def resolve_parameters(self, inputs: Dict[str, Any], agent: Agent, agent_step: AgentStep, **kwargs) -> Dict[str, Any]:
        """
        Returns a dict of input variable values.
        """
