import re
from typing import Any, Callable, Dict, Optional, Sequence, List, Tuple

from langchain import LLMChain, PromptTemplate
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import Document
from langchain.schema.language_model import BaseLanguageModel
from pydantic import BaseModel

SYSTEM_MESSAGE = """\
A question and a piece of context is given below.
Your task is to determine how relevant the context is to the given question by returning a relevance score. 
The relevance score is a number from 1-10 based on how relevant you think the context is to the question.
Return 0 if you think the context contains no information relevant to the question. Return 10 if you think the context contains all necessary information to answer the question in its entirety. Otherwise return a value between 0 and 10, depending on the relevance."""

HUMAN_MESSAGE = """\
QUESTION:
"{question}"

CONTEXT:
\"\"\"
{context}
\"\"\"

CONTEXT RELEVANCE SCORE BETWEEN 0 AND 10:"""


class LLMReranker(BaseModel):

    llm_chain: LLMChain

    @staticmethod
    def _get_input(query: str, doc: Document) -> Dict[str, Any]:
        """Return the chain input."""
        return {"question": query, "context": doc.page_content}

    def rerank_documents(
        self, documents: Sequence[Document], query: str
    ) -> Sequence[Document]:
        """Compress page content of raw documents."""
        docs: List[Tuple[float, Document]] = []
        for doc in documents:
            output = self.llm_chain.predict(**self._get_input(query, doc))
            score = float(re.findall(r'\d+', output)[0])
            if score == 0:
                continue
            #if score == 10:
                #return [doc]
            docs.append((score, doc))
        docs.sort(key=lambda x: x[0], reverse=True)
        for s, d in docs:
            print(f"{s}: {d.page_content[:32]}")
        return [d for s, d in docs]

    async def acompress_documents(
        self, documents: Sequence[Document], query: str
    ) -> Sequence[Document]:
        raise NotImplementedError

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel) -> "LLMReranker":
        """Initialize from LLM."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                SYSTEM_MESSAGE
            ),
            HumanMessagePromptTemplate.from_template(
                HUMAN_MESSAGE
            )
        ])
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt
        )
        return cls(llm_chain=llm_chain)