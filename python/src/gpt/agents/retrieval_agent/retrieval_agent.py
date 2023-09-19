from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import SystemMessagePromptTemplate
from langchain.retrievers import SelfQueryRetriever, MultiVectorRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.tools import Tool, StructuredTool
from langchain.vectorstores import AzureSearch, VectorStore
from pydantic.fields import FieldInfo

from gpt.agents.common.agent.base import Agent
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent

from langchain.pydantic_v1 import create_model
from typing import Dict, Any, Optional, Union, List

from gpt.chains.retrieval_chain.config import get_embeddings, get_vector_store, get_document_store
from gpt.chains.retrieval_chain.llm_filter.filter import LLMDocumentFilter
from gpt.chains.retrieval_chain.metadata_filter.filter_chain import MetadataFilterRetriever, QueryContext
from gpt.chains.retrieval_chain.multiquery_retriever.retriever import create_multi_query_retriever
from gpt.chains.retrieval_chain.parent_document_retriever.retriever import ParentDocumentRetriever
from gpt.chains.retrieval_chain.reranker.cohere_reranker import CohereThresholdRerank
from gpt.util.functions import json_schema_from_shorthand
from gpt.util.query_constructor.azure_search_translator import AzureCognitiveSearchTranslator


def json_schema_to_pydantic_model(name: str, schema: Dict[str, Any]) -> Any:
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list,
    }

    fields = {}
    for field_name, field_info in schema.items():
        field_type_str = field_info.get('type')
        field_type = type_mapping.get(field_type_str)
        if not field_info.get('required', True):
            field_type = Optional[field_type]
        if field_type is None:
            raise ValueError(f"Unsupported field type: {field_type_str}")

        field_description = field_info.get('description', '')
        # In Pydantic, the field definition is a tuple (type, default value).
        # Since the JSON schema doesn't specify a default value, we'll just use None.
        fields[field_name] = (field_type, FieldInfo(..., description=field_description))

    return create_model(name, **fields)

SYSTEM_MESSAGE = """\
Assistant is a helpful assistant that answers user questions and queries by calling functions to retrieve information from a document Q&A system.
The document Q&A system will answer given questions using available documents. 

Split up questions into multiple function calls where appropriate and combine the results.
If you can specify bike_model based on the input question, remove any mention of it from the query to document_qa_system.

If you can't find enough information to compile a meaningful and helpful answer for the user, don't say that the document or text does not provide enough information but just set the fields in store_final_result to null."""


def create_retrieval_agent(
    llm: BaseChatModel,
    database: str,
    database_url: str,
    embedding_provider: str,
    embedding_model: str,
    database_password: Optional[str] = None,
    output_schema: Optional[Dict[str, Union[str, dict]]] = None,
    multi_query_expansion: bool = False,
    reranker: Optional[str] = None,
    filter_metadata_field: Optional[str] = None,
    summary_index: Optional[str] = None,
    metadata_field_info: Optional[List[dict]] = None,
    document_content_description: Optional[str] = None,
    parent_document_store: Optional[str] = None,
    parent_document_store_url: Optional[str] = None,
    parent_document_store_password: Optional[str] = None,
    parent_document_store_namespace: Optional[str] = None,
    parent_document_id_key: str = "parent_id",
) -> Agent:
    agent = OpenAIFunctionsAgent.create(
        system_prompt_template=SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        llm=llm,
    )

    def query_docs(**query) -> str:
        embeddings = get_embeddings(embedding_provider, embedding_model)
        vector_store = get_vector_store(database, database_url, embeddings, password=database_password)

        # select child index to query using a summary index that contains a summary of the content of each child index
        if filter_metadata_field and summary_index and query[filter_metadata_field]:
            base_url, _ = database_url.rsplit('/', 1)
            summary_store = get_vector_store(database, base_url + "/" + summary_index, embeddings, password=database_password)

            if isinstance(summary_store, AzureSearch):
                f = summary_store.hybrid_search
            else:
                f = summary_store.similarity_search

            summary_index_query = query[filter_metadata_field]
            result = f(query=summary_index_query, k=1)[0]

            #child_index = result.metadata[summary_index]
            #vector_store = get_vector_store(database, base_url + "/" + child_index, embeddings, password=database_password)

            filter_value = result.metadata[filter_metadata_field]
            filter = {filter_metadata_field: filter_value}
        else:
            filter = None

        retrieval_qa = create_retrieval_qa(
            llm=llm,
            vector_store=vector_store,
            filter=filter,
            multi_query_expansion=multi_query_expansion,
            parent_document_id_key=parent_document_id_key,
            parent_document_store=parent_document_store,
            parent_document_store_namespace=parent_document_store_namespace,
            parent_document_store_password=parent_document_store_password,
            parent_document_store_url=parent_document_store_url,
            reranker=reranker,
            metadata_field_info=metadata_field_info,
            document_content_description=document_content_description
        )

        return retrieval_qa.run(query["query"])

    if filter_metadata_field and summary_index:
        qa_tool = StructuredTool.from_function(
            name="document_qa_system",
            description=f"Useful when you need to answer questions about the content of documents. Input should be a fully formed question and, if available, the {filter_metadata_field} (in that case don't mention it in the query). If no {filter_metadata_field} is mentioned, set it to null.",
            args_schema=json_schema_to_pydantic_model("document_qa_system",
                                                      {
                                                          "query": {
                                                              "description": f"the query without any mention of {filter_metadata_field}",
                                                              "type": "string"
                                                          },
                                                          filter_metadata_field: {
                                                              "description": f"the {filter_metadata_field} - if mentioned, else null",
                                                              "type": "string",
                                                              "required": False
                                                          }
                                                      }
            ),
            func=query_docs
        )
    else:
        qa_tool = StructuredTool.from_function(
            name="document_qa_system",
            description="Useful when you need to answer questions about the content of documents. Input should be a fully formed question.",
            func=query_docs,
            infer_schema=True
        )

    agent.add_tools([
        qa_tool,
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


def create_retrieval_qa(
    llm: BaseChatModel,
    vector_store: VectorStore,
    filter: Optional[dict] = None,
    multi_query_expansion: bool = False,
    reranker: Optional[str] = None,
    metadata_field_info: Optional[List[dict]] = None,
    document_content_description: Optional[str] = None,
    parent_document_store: Optional[str] = None,
    parent_document_store_url: Optional[str] = None,
    parent_document_store_password: Optional[str] = None,
    parent_document_store_namespace: Optional[str] = None,
    parent_document_id_key: str = "parent_id",
):
    init_k = 50
    top_n = 3

    # self-query on given metadata fields
    if metadata_field_info:
        # others are built-in
        query_translator = AzureCognitiveSearchTranslator() if isinstance(vector_store, AzureSearch) else None
        retriever = MetadataFilterRetriever.from_llm(
            llm,
            vector_store,
            document_content_description or "document",
            metadata_field_info,
            k=init_k,
            structured_query_translator=query_translator,
            use_original_query=False,
            verbose=True
        )
    else:
        retriever = vector_store.as_retriever(
            search_kwargs={
                'k': init_k,
                **({'filter': filter} if filter else {})
            }
        )

    # rephrase query multiple times and get union of docs
    if multi_query_expansion:
        retriever = create_multi_query_retriever(retriever=retriever, llm=llm)

    # resolve parent documents/larger chunks from embedded chunks
    if parent_document_store_url:
        store = get_document_store(
            parent_document_store,
            parent_document_store_url,
            parent_document_store_namespace,
            password=parent_document_store_password
        )
        retriever = ParentDocumentRetriever(
            n=init_k,
            child_retriever=retriever,
            docstore=store,
            id_key=parent_document_id_key,
        )

    transformers = []
    if reranker == 'cohere':
        cohere_reranker = CohereThresholdRerank(top_n=top_n)
        transformers.append(cohere_reranker)
    transformers.append(LLMDocumentFilter.from_llm(ChatOpenAI(temperature=0)))

    pipeline_compressor = DocumentCompressorPipeline(transformers=transformers)
    retriever = ContextualCompressionRetriever(
        base_compressor=pipeline_compressor,
        base_retriever=retriever
    )

    # answer synthesizer
    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    return retrieval_qa
