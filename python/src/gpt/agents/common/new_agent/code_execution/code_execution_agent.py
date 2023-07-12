from typing import Dict, Any, Optional, Callable, List, Sequence

from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate
from langchain.schema import AIMessage, FunctionMessage, HumanMessage
from langchain.vectorstores import VectorStore

from gpt.agents.common.code_execution.agent_functions import StoreFinalResultTool
from gpt.agents.common.code_execution.prompt import SYSTEM_MESSAGE_FUNCTIONS, DEFAULT_FEW_SHOT_PROMPT_MESSAGES
from gpt.agents.common.code_execution.tool import PythonREPLTool
from gpt.agents.common.code_execution.util import create_func_obj, get_python_functions_descriptions
from gpt.agents.common.new_agent.base import AgentParameterResolver, Agent
from gpt.agents.common.new_agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.new_agent.openai_functions.output_parser import OpenAIFunctionsOutputParser
from gpt.agents.common.new_agent.output_parser import AgentOutputParser
from gpt.agents.common.new_agent.step import AgentStep
from gpt.agents.common.new_agent.toolbox import Toolbox


class CodeExecutionParameterResolver(AgentParameterResolver):

    skill_store: Optional[VectorStore] = None
    n_skills = 5
    skill_relevance_threshold = 0.3

    class Config:
        arbitrary_types_allowed = True

    def resolve_parameters(self, inputs: Dict[str, Any], agent: Agent, agent_step: AgentStep, **kwargs) -> Dict[str, Any]:
        python_tool: PythonREPLTool = agent.toolbox.get_tool("python")
        functions = [*python_tool.functions]

        if self.skill_store:
            relevant_skill_documents = self.skill_store.similarity_search_with_relevance_scores(
                query=inputs['input'],
                k=self.n_skills
            )
            relevant_skill_documents = [s[0] for s in relevant_skill_documents if s[1] > self.skill_relevance_threshold]
            skill_functions_strs = [s.metadata['function'] for s in relevant_skill_documents]

            updated_python_tool = PythonREPLTool.from_functions(functions, skill_functions_strs)
            agent.toolbox.add_tool(updated_python_tool)

            skill_functions = [create_func_obj(s.metadata['function'], s.metadata['comment']) for s in relevant_skill_documents]
            functions += skill_functions

        return {
            "input": inputs["input"],
            # "context": inputs["context"],
            "functions": get_python_functions_descriptions(functions),
            "transcript": agent_step.transcript,
        }


class PythonCodeExecutionAgent(OpenAIFunctionsAgent):

    def __init__(
        self,
        llm: ChatOpenAI,
        python_functions: Optional[Sequence[Callable]] = None,
        skill_store: Optional[VectorStore] = None,
        system_prompt_template: Optional[SystemMessagePromptTemplate] = None,
        user_prompt_template: Optional[HumanMessagePromptTemplate] = None,
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None,
        max_steps: int = 10
    ):
        python_tool = PythonREPLTool.from_functions(python_functions or [])
        final_tool = StoreFinalResultTool(repl=python_tool) # todo repl in final tool is not updated with skill, so this approach is bad
        super().__init__(
            llm=llm,
            system_prompt_template=system_prompt_template or SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE_FUNCTIONS),
            user_prompt_template=user_prompt_template or HumanMessagePromptTemplate.from_template("{input}"),
            few_shot_prompt_messages=few_shot_prompt_messages or DEFAULT_FEW_SHOT_PROMPT_MESSAGES,
            prompt_parameters_resolver=CodeExecutionParameterResolver(skill_store=skill_store),
            output_parser=OpenAIFunctionsOutputParser(final_tool=final_tool),
            toolbox=Toolbox([python_tool, final_tool]),
            stop_words=None,
            max_steps=max_steps
        )
