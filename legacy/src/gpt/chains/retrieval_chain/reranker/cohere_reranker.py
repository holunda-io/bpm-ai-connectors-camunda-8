from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Sequence

from langchain.callbacks.manager import Callbacks
from langchain.pydantic_v1 import Extra, root_validator
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from langchain.schema import Document
from langchain.utils import get_from_dict_or_env

from gpt.chains.retrieval_chain.metadata_filter.filter_chain import QueryContext


class CohereThresholdRerank(BaseDocumentCompressor):
    """Document compressor that uses `Cohere Rerank API`."""

    top_n: int = 3
    k: int = 10

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Compress documents using Cohere's rerank API.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        if len(documents) == 0:
            return []

        cohere_rerank = CohereRerank(top_n=self.k)
        reranked_docs = cohere_rerank.compress_documents(documents, query)

        avg_score = sum(d.metadata['relevance_score'] for d in reranked_docs) / len(reranked_docs)
        print("======================")
        print(f"Cutoff score: {avg_score}")
        print("======================")
        reranked_docs_top = reranked_docs[:self.top_n]
        reranked_docs_top = [d for d in reranked_docs_top if d.metadata["relevance_score"] >= avg_score]
        return reranked_docs_top

    async def acompress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        raise NotImplementedError()
