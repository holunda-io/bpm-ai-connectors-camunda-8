from inspect import signature
from typing import Any, Optional
from typing import List, Sequence, Tuple, Callable

from langchain import LLMChain
from langchain.agents import Agent, AgentOutputParser
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import (
    AgentAction, BaseMessage, AIMessage, HumanMessage, )

from gpt.agents.common.code_execution.output_parser import PythonCodeAgentOutputParser
from gpt.agents.common.code_execution.prompt import CODE_RESPONSE_TEMPLATE, SYSTEM_MESSAGE, HUMAN_MESSAGE


class PythonReplAgent(Agent):

    functions: Sequence[Callable]

    template_function_response: str = CODE_RESPONSE_TEMPLATE
    output_key: str = "output"

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
        return ["DUMMY_STOP"]  # todo

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

    @classmethod
    def create_prompt(
            cls,
            functions: Sequence[Callable],
            system_message: str = SYSTEM_MESSAGE,
            human_message: str = HUMAN_MESSAGE,
            input_variables: Optional[List[str]] = None,
    ) -> BasePromptTemplate:
        function_descriptions = "\n".join(
            [f"- {f.__name__}{signature(f)}:\n{f.__doc__}" for f in functions]
        )
        system_prompt = system_message.format(
            functions=function_descriptions
        )
        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_message),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        return ChatPromptTemplate.from_messages(messages)

    @classmethod
    def from_llm_and_functions(
        cls,
        llm: BaseLanguageModel,
        functions: Sequence[Callable],
        callback_manager: Optional[BaseCallbackManager] = None,
        system_message: str = SYSTEM_MESSAGE,
        human_message: str = HUMAN_MESSAGE,
        input_variables: Optional[List[str]] = None,
        output_key: str = "output",
        **kwargs: Any,
    ) -> "PythonReplAgent":
        """Construct agent from an LLM and functions."""
        prompt = cls.create_prompt(
            functions,
            system_message=system_message,
            human_message=human_message,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )
        return cls(
            functions=functions,
            llm_chain=llm_chain,
            output_parser=PythonCodeAgentOutputParser(functions=functions),
            output_key=output_key,
            stop=[],
            **kwargs,
        )

    @property
    def _agent_type(self) -> str:
        raise "code_execution"
