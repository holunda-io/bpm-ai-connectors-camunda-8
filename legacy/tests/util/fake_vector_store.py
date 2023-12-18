import logging
from typing import List, Optional, Dict, Tuple, Any, Iterable
from abc import ABC, abstractmethod

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import VectorStore


class FakeVectorStore(VectorStore):
    def __init__(self):
        self.documents = []  # Store documents
        self.search_history = []  # To remember searches

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any
    ) -> List[str]:
        ids = []
        for i, text in enumerate(texts):
            doc_id = str(len(self.documents) + i)
            metadata = metadatas[i] if metadatas else {}
            self.documents.append(Document(page_content=text, metadata=metadata, id=doc_id))
            ids.append(doc_id)
        return ids

    def delete(self, ids: Optional[List[str]] = None, **kwargs: Any) -> Optional[bool]:
        if not ids:
            return False
        self.documents = [doc for doc in self.documents if doc.id not in ids]
        return True

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        self.search_history.append(query)
        return [doc for doc in self.documents if query in doc.page_content][:k]

    @classmethod
    def from_texts(cls, texts: List[str], embedding: Embeddings, metadatas: Optional[List[dict]] = None, **kwargs: Any) -> 'FakeVectorStore':
        store = FakeVectorStore()
        store.add_texts(texts, metadatas)
        return store

    def search_was_made(self, keyword: str) -> bool:
        """Check if a search containing the given keyword was made."""
        return any(keyword in search for search in self.search_history)
