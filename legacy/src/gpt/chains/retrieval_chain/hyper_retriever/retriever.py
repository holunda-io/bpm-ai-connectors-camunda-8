import uuid
from typing import List, Optional, Dict, Union

from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.chat_models.base import BaseChatModel
from langchain.pydantic_v1 import Field
from langchain.schema import BaseRetriever, BaseStore, Document
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import VectorStore, AzureSearch

from gpt.config import get_embeddings, get_vector_store
from gpt.chains.retrieval_chain.metadata_filter.filter_chain import MetadataFilterRetriever
from gpt.util.query_constructor.azure_search_translator import AzureCognitiveSearchTranslator


class HyperRetriever(BaseRetriever):

    llm: BaseChatModel
    database: str
    database_url: str
    embedding_provider: str
    embedding_model: str
    database_password: Optional[str] = None
    output_schema: Optional[Dict[str, Union[str, dict]]] = None
    multi_query_expansion: bool = False
    metadata_field_info: Optional[List[dict]] = None
    document_content_description: Optional[str] = None
    parent_document_store: Optional[str] = None
    parent_document_store_url: Optional[str] = None
    parent_document_store_password: Optional[str] = None
    parent_document_store_namespace: Optional[str] = None
    parent_document_id_key: str = "parent_id"

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        embeddings = get_embeddings(self.embedding_provider, self.embedding_model)
        vector_store = get_vector_store(self.database, self.database_url, embeddings, password=self.database_password)

        # self-query on given metadata fields
        if self.metadata_field_info:
            # others are built-in
            query_translator = AzureCognitiveSearchTranslator() if isinstance(vector_store, AzureSearch) else None
            retriever = MetadataFilterRetriever.from_llm(
                self.llm,
                vector_store,
                self.document_content_description or "document",
                self.metadata_field_info,
                k=15,
                structured_query_translator=query_translator,
                use_original_query=False,
                verbose=True
            )
        else:
            retriever = vector_store.as_retriever()

        base_docs = retriever.get_relevant_documents(query)

