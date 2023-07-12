import json
from json import JSONDecodeError
from typing import Any, List, Optional, Sequence, Tuple, Union, Callable, Type

from langchain import LLMChain, PromptTemplate
from langchain.agents import BaseSingleActionAgent, AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent, _format_intermediate_steps, _FunctionsAgentAction
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import Callbacks, CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    BaseMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder, SystemMessagePromptTemplate, AIMessagePromptTemplate, ChatMessagePromptTemplate,
)
from langchain.schema import (
    AgentAction,
    AgentFinish,
    BaseMessage, AIMessage, OutputParserException,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from gpt.agents.common.code_execution.prompt import CODE_RESPONSE_TEMPLATE, SYSTEM_MESSAGE, HUMAN_MESSAGE, SYSTEM_MESSAGE_FUNCTIONS
from gpt.agents.common.code_execution.tool import PythonREPLTool
from gpt.agents.common.code_execution.util import get_python_functions_descriptions
from langchain.tools import tool


class StoreFinalResultSchema(BaseModel):
    function_def: str = Field(description="generic python function definition")
    function_call: str = Field(description="concrete call")


class StoreFinalResultTool(BaseTool):

    name = "store_final_result"
    description = "Stores the final python function definition and call."
    args_schema: Type[StoreFinalResultSchema] = StoreFinalResultSchema
    return_direct = True

    repl: PythonREPLTool

    @classmethod
    def from_repl(cls, repl: PythonREPLTool):
        return cls(repl=repl)

    def _run(
        self,
        function_def: str,
        function_call: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.repl.run(function_def + '\n' + function_call)

    async def _arun(
        self,
        function_def: str,
        function_call: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool asynchronously."""
        raise self.repl.run(function_def + '\n' + function_call)


class PythonReplFunctionsAgent(OpenAIFunctionsAgent):

    python_functions: Sequence[Callable]
    python_skill_functions: Sequence[Callable] = []

    llm: BaseLanguageModel
    system_message: str
    human_message: str

    template_function_response: str = CODE_RESPONSE_TEMPLATE
    output_key: str = "output"

    def get_all_python_functions(self):
        return [*self.python_functions, *self.python_skill_functions]

    @property
    def return_values(self) -> List[str]:
        """Return values of the agent."""
        return [self.output_key]

    @property
    def input_keys(self) -> List[str]:
        """The input keys."""
        return list(set(self.prompt.input_variables) - {"agent_scratchpad"})

    def create_prompt(
        self,
        system_message_template: str = SYSTEM_MESSAGE_FUNCTIONS,
        human_message_template: str = HUMAN_MESSAGE,
    ) -> BasePromptTemplate:
        system_prompt = PromptTemplate(
            template=system_message_template,
            input_variables=[],
            partial_variables={"functions": get_python_functions_descriptions(self.get_all_python_functions())}
        )

        messages = [
            SystemMessagePromptTemplate(prompt=system_prompt),
            HumanMessagePromptTemplate.from_template("Calculate 10 + 15"),
            AIMessagePromptTemplate.from_template("We can calculate this using a python math expression:", additional_kwargs={"function_call": {"name": "python", "arguments": '{ "input": "10 + 15" }'}}),
            ChatMessagePromptTemplate.from_template(role="function", template="25", additional_kwargs={"name": "python"}),
            AIMessagePromptTemplate.from_template("Great. Now let's wrap this in a re-usable function:", additional_kwargs={"function_call": {"name": "store_final_result", "arguments": '{ "function_def": "def add_two_numbers(a, b):\n    return a + b", "function_call": "add_two_numbers(10, 15)" }'}}),
            ChatMessagePromptTemplate.from_template(role="function", template="Result stored. Continue with next task.", additional_kwargs={"name": "python"}),
            HumanMessagePromptTemplate.from_template(human_message_template),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        return ChatPromptTemplate.from_messages(messages=messages)

    def _parse_ai_message(self, message: BaseMessage) -> Union[AgentAction, AgentFinish]:
        """Parse an AI message."""
        if not isinstance(message, AIMessage):
            raise TypeError(f"Expected an AI message got {type(message)}")

        function_call = message.additional_kwargs.get("function_call", {})

        if function_call:
            function_name = function_call["name"]
            try:
                _tool_input = json.loads(function_call["arguments"], strict=False)
            except JSONDecodeError:
                raise OutputParserException(
                    f"Could not parse tool input: {function_call} because "
                    f"the `arguments` is not valid JSON."
                )

            # HACK HACK HACK:
            # The code that encodes tool input into Open AI uses a special variable
            # name called `__arg1` to handle old style tools that do not expose a
            # schema and expect a single string argument as an input.
            # We unpack the argument here if it exists.
            # Open AI does not support passing in a JSON array as an argument.
            if "__arg1" in _tool_input:
                tool_input = _tool_input["__arg1"]
            else:
                tool_input = _tool_input

            content_msg = "responded: {content}\n" if message.content else "\n"

            return _FunctionsAgentAction(
                tool=function_name,
                tool_input=tool_input,
                log=f"\nInvoking: `{function_name}` with `{tool_input}`\n{content_msg}\n",
                message_log=[message],
            )

        return AgentFinish(return_values={self.output_key: message.content}, log=message.content)

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        prompt = self.create_prompt(
            system_message_template=self.system_message,
            human_message_template=self.human_message,
        )

        agent_scratchpad = _format_intermediate_steps(intermediate_steps)
        prompt = prompt.format_prompt(
            **kwargs, agent_scratchpad=agent_scratchpad
        )
        messages = prompt.to_messages()
        predicted_message = self.llm.predict_messages(
            messages, functions=self.functions, callbacks=callbacks
        )
        agent_decision = self._parse_ai_message(predicted_message)
        return agent_decision

    @classmethod
    def from_llm_and_python_functions(
        cls,
        llm: BaseLanguageModel,
        python_functions: Sequence[Callable],
        system_message: str = SYSTEM_MESSAGE_FUNCTIONS,
        human_message: str = HUMAN_MESSAGE,
        output_key: str = "output",
        callback_manager: Optional[BaseCallbackManager] = None,
        **kwargs: Any,
    ) -> "PythonReplFunctionsAgent":
        """Construct an agent from an LLM and tools."""
        if not isinstance(llm, ChatOpenAI):
            raise ValueError("Only supported with OpenAI models.")
        repl_tool = PythonREPLTool.from_functions(python_functions)
        return cls(
            llm=llm,
            system_message=system_message,
            human_message=human_message,
            python_functions=python_functions,
            prompt=PromptTemplate.from_template("{agent_scratchpad}"),
            tools=[repl_tool, StoreFinalResultTool.from_repl(repl=repl_tool)],
            callback_manager=callback_manager,
            output_key=output_key,
            **kwargs,
        )
