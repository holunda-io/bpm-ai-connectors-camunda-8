from typing import Any, Dict, Optional

from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import VectorStore

from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent
from gpt.agents.common.agent.code_execution.util import generate_function_stub
from gpt.agents.common.agent.memory import AgentMemory
from gpt.agents.openapi_agent.code_execution.functions import get_api_functions
from gpt.agents.openapi_agent.code_execution.prompt import create_user_prompt_messages, create_few_shot_messages


def create_openapi_code_execution_agent(
    llm: ChatOpenAI,
    api_spec_url: str,
    skill_store: Optional[VectorStore] = None,
    llm_call: bool = True,
    enable_skill_creation: bool = False,
    output_schema: Optional[Dict[str, Any]] = None,
    agent_memory: Optional[AgentMemory] = None
) -> PythonCodeExecutionAgent:
    type_definitions, fun_names, _locals = get_api_functions(api_spec_url)

    #function_stub = generate_function_stub({"prefix": "reversed: "}, output_schema)

    return PythonCodeExecutionAgent.from_functions(
        llm=llm,
        python_functions=[f for n, f in _locals.items() if n in fun_names],
        additional_python_definitions=[type_definitions],
        user_prompt_templates=create_user_prompt_messages(llm_call, stub_function=(output_schema or not llm_call)),
        #few_shot_prompt_messages=create_few_shot_messages(function_stub, llm_call),
        enable_skill_creation=enable_skill_creation,
        skill_store=skill_store,
        llm_call=llm_call,
        output_schema=output_schema,
        agent_memory=agent_memory
    )
