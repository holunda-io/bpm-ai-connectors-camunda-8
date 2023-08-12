from langchain.chains import RetrievalQA
from langchain.chains.base import Chain
from langchain.chat_models.base import BaseChatModel
from langchain.retrievers import MultiQueryRetriever
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.chains.retrieval_chain.chain import get_embeddings, get_vector_store
from gpt.chains.retrieval_chain.prompt import MULTI_QUERY_PROMPT

from pydantic import create_model
from typing import Dict, Any, Optional, Union

from gpt.util.functions import json_schema_from_shorthand


def json_schema_to_pydantic_model(name: str, schema: Dict[str, Any]) -> Any:
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list
    }

    fields = {}
    for field_name, field_info in schema.items():
        field_type_str = field_info.get('type')
        field_type = type_mapping.get(field_type_str)
        if field_type is None:
            raise ValueError(f"Unsupported field type: {field_type_str}")

        field_description = field_info.get('description', '')
        # In Pydantic, the field definition is a tuple (type, default value).
        # Since the JSON schema doesn't specify a default value, we'll just use None.
        fields[field_name] = (field_type, FieldInfo(..., description=field_description))

    return create_model(name, **fields)


def create_retrieval_agent(
    llm: BaseChatModel,
    database_url: str,
    embedding_provider: str,
    embedding_model: str,
    output_schema: Optional[Dict[str, Union[str, dict]]] = None,
) -> Chain:
    agent = OpenAIFunctionsAgent.create(
        llm=llm,
    )

    embeddings = get_embeddings(embedding_provider, embedding_model)
    vector_store = get_vector_store(database_url, embeddings)

    # rephrase query multiple times and get union of docs
    # multi_retriever = MultiQueryRetriever.from_llm(
    #     retriever=vector_store.as_retriever(),
    #     llm=llm,
    #     prompt=MULTI_QUERY_PROMPT
    # )
    # answer synthesizer
    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
    )

    def query_docs(question: str) -> str:
        """Useful for when you need to answer questions about the content of documents. Input should be a fully formed question."""
        return retrieval_qa.run(question)

    agent.add_tools([
        StructuredTool.from_function(
            name="document_qa_system",
            func=query_docs,
            infer_schema=True
        ),
        StructuredTool.from_function(
            name="store_final_result",
            func=lambda x: x,
            description="Stores the final answer to the query.",
            return_direct=True,
            args_schema=json_schema_to_pydantic_model("final_result", json_schema_from_shorthand(output_schema) if output_schema else {"answer": {
                "description": "the answer text",
                "type": "string"
            }})
        )
    ])
    return agent
