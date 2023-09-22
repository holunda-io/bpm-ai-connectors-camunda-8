from langchain.embeddings import FakeEmbeddings
from langchain.schema import AIMessage

from gpt.agents.retrieval_agent.retrieval_agent import create_retrieval_agent
from util.fake_chat_llm import FakeChatOpenAI
from util.fake_vector_store import FakeVectorStore


def get_tool_calls():
    return [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "document_qa_system", "arguments": '{ "query": "foo" }'}}
        ),
        AIMessage(
            content="According to the context: foo is bar"
        )
    ]


def get_fake_llm():
    return FakeChatOpenAI(responses=get_tool_calls() + [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "store_final_result", "arguments": '{ "answer": "foo is bar" }'}}
        )
    ])

def get_fake_filter_llm():
    return FakeChatOpenAI(responses=[
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "RecordDecision", "arguments": '{ "context_is_relevant": true }'}}
        )
    ])


def test_retrieval_agent():
    fake_vector_store = FakeVectorStore.from_texts(
        texts=["foo is bar"],
        embedding=FakeEmbeddings(size=1)
    )

    agent = create_retrieval_agent(
        llm=get_fake_llm(),
        filter_llm=get_fake_filter_llm(),
        vector_store=fake_vector_store
    )

    result = agent.run(input="What is foo?", context="")["output"]

    assert "bar" in result["answer"]