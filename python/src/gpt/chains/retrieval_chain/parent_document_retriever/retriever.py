import uuid
from typing import List, Optional

from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.pydantic_v1 import Field
from langchain.schema import BaseRetriever, BaseStore, Document
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import VectorStore


class ParentDocumentRetriever(BaseRetriever):
    """Retrieve from a set of multiple embeddings for the same document."""

    child_retriever: BaseRetriever
    """The underlying vectorstore to use to store small chunks
    and their embedding vectors"""
    docstore: BaseStore[str, str]
    """The storage layer for the parent documents"""
    id_key: str = "doc_id"
    search_kwargs: dict = Field(default_factory=dict)
    """Keyword arguments to pass to the search function."""

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        sub_docs = self.child_retriever.get_relevant_documents(query, **self.search_kwargs)
        print(f"Found {len(sub_docs)} sub documents.")

        # Count the number of sub_docs pointing to each parent_doc
        id_counts = {}
        for d in sub_docs:
            parent_id = d.metadata[self.id_key]
            if parent_id not in id_counts:
                id_counts[parent_id] = 0
            id_counts[parent_id] += 1

        # If there's at least one parent_doc with id_count > 1, prune those with id_count = 1
        if any(count > 1 for count in id_counts.values()):
            id_counts = {k: v for k, v in id_counts.items() if v > 1}

        # Sort the parent_doc ids based on their counts in descending order
        sorted_ids = sorted(id_counts.keys(), key=lambda x: id_counts[x], reverse=True)

        # Take the top 3 most relevant parent_doc ids
        top_ids = sorted_ids[:4]

        # Fetch the content of these parent_docs
        doc_contents = self.docstore.mget(top_ids)

        print("Counts for the top 3 parent documents:")
        for idx, parent_id in enumerate(top_ids, 1):
            print(f"#{idx}: Parent ID {parent_id} - Child hit count: {id_counts[parent_id]}")

        return [Document(page_content=c) for c in doc_contents if c is not None]

    def _get_relevant_documents_old(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        sub_docs = self.child_retriever.get_relevant_documents(query, **self.search_kwargs)
        # We do this to maintain the order of the ids that are returned
        ids = []
        for d in sub_docs:
            if d.metadata[self.id_key] not in ids:
                ids.append(d.metadata[self.id_key])
        doc_contents = self.docstore.mget(ids)

        print(f"Found {len(doc_contents)} parent documents.")
        return [Document(page_content=c) for c in doc_contents if c is not None]

    @staticmethod
    def add_documents(
        documents: List[Document],
        id_key: str,
        docstore: BaseStore[str, str],
        vectorstore: VectorStore,
        child_splitter: TextSplitter,
        parent_splitter: Optional[TextSplitter] = None,
        ids: Optional[List[str]] = None,
        add_to_docstore: bool = True,
    ) -> None:
        """Adds documents to the docstore and vectorstores.

        Args:
            documents: List of documents to add
            ids: Optional list of ids for documents. If provided should be the same
                length as the list of documents. Can provided if parent documents
                are already in the document store and you don't want to re-add
                to the docstore. If not provided, random UUIDs will be used as
                ids.
            add_to_docstore: Boolean of whether to add documents to docstore.
                This can be false if and only if `ids` are provided. You may want
                to set this to False if the documents are already in the docstore
                and you don't want to re-add them.
        """
        if parent_splitter is not None:
            documents = parent_splitter.split_documents(documents)
        if ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in documents]
            if not add_to_docstore:
                raise ValueError(
                    "If ids are not passed in, `add_to_docstore` MUST be True"
                )
        else:
            if len(documents) != len(ids):
                raise ValueError(
                    "Got uneven list of documents and ids. "
                    "If `ids` is provided, should be same length as `documents`."
                )
            doc_ids = ids

        docs = []
        full_docs = []
        for i, doc in enumerate(documents):
            _id = doc_ids[i]
            sub_docs = child_splitter.split_documents([doc])
            for _doc in sub_docs:
                _doc.metadata[id_key] = _id
            docs.extend(sub_docs)
            full_docs.append((_id, doc.page_content))
        vectorstore.add_documents(docs)
        if add_to_docstore:
            docstore.mset(full_docs)