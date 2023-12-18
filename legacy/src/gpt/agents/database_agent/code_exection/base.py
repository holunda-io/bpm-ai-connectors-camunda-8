from typing import Any, Dict, Optional

from langchain import SQLDatabase
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import VectorStore

from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent
from gpt.agents.common.agent.code_execution.util import generate_function_stub
from gpt.agents.common.agent.memory import AgentMemory
from gpt.agents.database_agent.code_exection.functions import get_database_functions
from gpt.agents.database_agent.code_exection.prompt import create_user_prompt_messages, create_few_shot_messages


def create_database_code_execution_agent(
    llm: ChatOpenAI,
    database_url: str,
    skill_store: Optional[VectorStore] = None,
    llm_call: bool = True,
    enable_skill_creation: bool = False,
    output_schema: Optional[Dict[str, Any]] = None,
    agent_memory: Optional[AgentMemory] = None
) -> PythonCodeExecutionAgent:
    db = SQLDatabase.from_uri(database_url)
    tables_str = ", ".join(db.get_usable_table_names())
    function_stub = generate_function_stub({"prefix": "reversed: "}, output_schema)
    return PythonCodeExecutionAgent.from_functions(
        llm=llm,
        python_functions=get_database_functions(llm, db),
        user_prompt_templates=create_user_prompt_messages(tables_str, llm_call, stub_function=(output_schema or not llm_call)),
        few_shot_prompt_messages=create_few_shot_messages(tables_str, function_stub, llm_call),
        enable_skill_creation=enable_skill_creation,
        skill_store=skill_store,
        llm_call=llm_call,
        output_schema=output_schema,
        agent_memory=agent_memory
    )
