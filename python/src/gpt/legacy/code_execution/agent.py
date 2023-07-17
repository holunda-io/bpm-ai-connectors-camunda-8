from typing import Any, Union, Dict
from typing import List, Sequence, Tuple, Callable

from langchain import LLMChain, PromptTemplate
from langchain.agents import Agent, AgentOutputParser
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import Callbacks
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import (
    AgentAction, BaseMessage, AIMessage, HumanMessage, AgentFinish, )
from pydantic import root_validator

from gpt.legacy.code_execution.output_parser import PythonCodeAgentOutputParser
from gpt.agents.common.agent.code_execution.prompt import CODE_RESPONSE_TEMPLATE, SYSTEM_MESSAGE, HUMAN_MESSAGE
from gpt.agents.common.agent.code_execution.util import get_python_functions_descriptions


class PythonReplAgent(Agent):

    functions: Sequence[Callable]
    skill_functions: Sequence[Callable] = []

    llm: BaseLanguageModel
    llm_chain: LLMChain
    system_message: str
    human_message: str

    template_function_response: str = CODE_RESPONSE_TEMPLATE
    output_key: str = "output"

    def get_all_functions(self):
        return [*self.functions, *self.skill_functions]

    @property
    def return_values(self) -> List[str]:
        return [self.output_key]

    @property
    def observation_prefix(self) -> str:
        return ""  # todo

    @property
    def llm_prefix(self) -> str:
        return ""  # todo

    @property
    def _stop(self) -> List[str]:
        return ["```\n"]

    @classmethod
    def _get_default_output_parser(cls, **kwargs: Any) -> AgentOutputParser:
        return PythonCodeAgentOutputParser()

    def _construct_scratchpad(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> List[BaseMessage]:
        """Construct the scratchpad that lets the agent continue its thought process."""
        thoughts: List[BaseMessage] = []
        for action, observation in intermediate_steps:
            thoughts.append(AIMessage(
                content=action.log
            ))
            thoughts.append(HumanMessage(
                content=self.template_function_response.format(observation=observation)
            ))
        return thoughts

    @root_validator()
    def validate_prompt(cls, values: Dict) -> Dict:
        return values

    def create_prompt(
            self,
            system_message: str = SYSTEM_MESSAGE,
            human_message: str = HUMAN_MESSAGE,
    ) -> BasePromptTemplate:
        system_prompt = PromptTemplate(
            template=system_message,
            input_variables=[],
            partial_variables={"functions": get_python_functions_descriptions(self.get_all_functions())}
        )
        messages = [
            SystemMessagePromptTemplate(prompt=system_prompt),
            HumanMessagePromptTemplate.from_template(human_message),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        return ChatPromptTemplate.from_messages(messages)

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        prompt = self.create_prompt(
            system_message=self.system_message,
            human_message=self.human_message,
        )
        self.llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )
        return super().plan(intermediate_steps, callbacks, **kwargs)

    @classmethod
    def from_llm_and_functions(
        cls,
        llm: BaseLanguageModel,
        functions: Sequence[Callable],
        system_message: str = SYSTEM_MESSAGE,
        human_message: str = HUMAN_MESSAGE,
        output_key: str = "output",
        **kwargs: Any,
    ) -> "PythonReplAgent":
        """Construct agent from an LLM and functions."""
        return cls(
            llm=llm,
            llm_chain=LLMChain(llm=llm, prompt=PromptTemplate.from_template("")),
            system_message=system_message,
            human_message=human_message,
            functions=functions,
            output_parser=PythonCodeAgentOutputParser(functions=functions),
            output_key=output_key,
            stop=[],
            **kwargs,
        )

    @property
    def _agent_type(self) -> str:
        raise "code_execution"
