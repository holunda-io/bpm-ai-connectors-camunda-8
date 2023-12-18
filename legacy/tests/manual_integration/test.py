import json
import os
from typing import List, Tuple

import langchain
import pytest
from langchain import Cohere, SQLDatabase
from langchain.cache import SQLiteCache
from langchain.chains import RetrievalQA, FlareChain
from langchain.chat_models import ChatOpenAI, ChatCohere
from langchain.document_loaders import WebBaseLoader, PyPDFLoader, OnlinePDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AlephAlpha
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.utilities.openapi import OpenAPISpec
from langchain.vectorstores import Chroma, Weaviate

from gpt.agents.common.agent.code_execution.skill_creation.comment_chain import create_code_comment_chain
from gpt.agents.common.agent.code_execution.skill_creation.eval_chain import create_code_eval_chain
from gpt.agents.common.agent.code_execution.util import get_python_functions_descriptions
from gpt.agents.database_agent.agent import create_database_agent
from gpt.agents.retrieval_agent.retrieval_agent import create_retrieval_agent
from gpt.chains.compose_chain.chain import create_compose_chain
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.generic_chain.chain import create_generic_chain
from gpt.chains.retrieval_chain.chain import create_legacy_retrieval_chain
from gpt.chains.support.flare_instruct.base import FLAREInstructChain
from agents.openapi_agent.openapi_spec import get_test_api_spec_str_for_url

langchain.llm_cache = SQLiteCache(database_path=".langchain-test.db")

from gpt.config import get_openai_chat_llm, LUMINOUS_SUPREME_CONTROL, get_vector_store, get_embeddings, \
    get_document_store
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.agents.plan_and_execute.executor.executor import create_executor
from gpt.chains.translate_chain.chain import create_translate_chain
from langchain.chains.openai_functions.openapi import get_openapi_chain, openapi_spec_to_openai_fn


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_openapi_agent():
    agent = create_openapi_agent(
        llm=get_openai_chat_llm(model_name="gpt-4"),
        api_spec_url="http://localhost:8090/v3/api-docs"
    )
    result = agent.run(
        query="Return the details of the customer.",
        context='{"customerId": 1}',
        output_schema='{"email": "the email", "name": "firstname and lastname"}'
    )
    print(result)
    assert "max.mustermann@mail.com" in result


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_database_agent():
    agent = create_database_agent(
        llm=get_openai_chat_llm(model_name="gpt-4"),
        database_url='postgresql://postgres:postgres@localhost:5438/postgres'
    )
    result = agent.run(
        input="Return the details of the customer.",
        context='{"customerId": 1}',
        output_schema='{"street": "the street and number in format `street number`", "name": "lastname, firstname"}'
    )
    print(result)
    assert "Burks, Debra" in result
    assert "Thorne Ave. 9273" in result


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_executor():
    executor = create_executor(
        llm=get_openai_chat_llm(model_name="gpt-3.5-turbo"),
        tools={"get_details": "Get details about a customer."}
    )
    result = executor.run(
        task="Return the details of the customer.",
        context='{"customerId": 1}',
        previous_steps='[]',
        current_step='Get the name of the customer'
    )
    print(result)


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_extract():
    schema = {
        "name": "the first name only",
        "toys": {"type": "integer", "description": "number of wooden toys"},
        "birthday": {"type": "string", "description": "birthday in format: dd_mm_yyyy"}
    }
    chain = create_extract_chain(
        schema,
        get_openai_chat_llm(model_name="gpt-4-0613"),
        repeated=False
    )
    print(schema)
    print(chain.run(
        '{"text": "My name is Johnny Johnson and I go to ABC Kindergarden (2 miles away) and I am 2 years old. My birthday is on the 6th of November, I was born in 2021. I have 5 toys, 3 of which are made from wood. The other two are metal." }'
    ))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_extract_repeated():
    schema = {
        "firstname": "the first name",
        "lastname": {"type": "string", "description": "the last name"},
        "age": {"type": "integer", "description": "age in full years"}
    }
    chain = create_extract_chain(
        schema,
        get_openai_chat_llm(model_name="gpt-3.5-turbo"),
        repeated=True
    )
    print(schema)
    print(chain.run(
        '{"text": "My name is Johnny Johnson and my birthday is on the 6th of November. My friends are James Miller (13), Max Meier which is 11 and a half years old, and finally Bob - 12 years old." }'
    ))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_decide():
    context = {
          "riddle": """\
Riddle me this: 
Penny has 5 children. 
The 1st is named January.
 2nd kid is February. 
Her 3rd is called March. 
4th is April. 
What is the name of the 5th."""
    }

    chain = create_decide_chain(
        get_openai_chat_llm(model_name="gpt-4"),
        instructions="What is the solution to the riddle?",
        output_type="string",
        possible_values=[],
        strategy="cot"
    )
    print(chain.run(input=context))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_decide_standard():
    context = {
        "firstname": "Max",
        "lastname": "Meier",
        "age": "39",
        "qualifications": ["Went to highschool.","Has a ton of friends.", "Very wealthy.", "CS degree."],
    }
    chain = create_decide_chain(
        #AlephAlpha(model=LUMINOUS_SUPREME_CONTROL),
        ChatCohere(temperature=0, max_tokens=1024),
        instructions="Decide if the applicant is qualified for the job as CTO.",
        output_type="string",
        possible_values=["QUALIFIED", "NOT_QUALIFIED"]
    )
    print(chain.run(input=context))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_translate():
    input = {
        "name": "OpenAI",
        "description": "OpenAI is an American artificial intelligence (AI) research laboratory consisting of the non-profit OpenAI Incorporated and its for-profit subsidiary corporation OpenAI Limited Partnership.",
        "motive": 'Some scientists, such as Stephen Hawking and Stuart Russell, have articulated concerns that if advanced AI someday gains the ability to re-design itself at an ever-increasing rate, an unstoppable "intelligence explosion" could lead to human extinction. Co-founder Musk characterizes AI as humanity\'s "biggest existential threat".',
    }
    chain = create_translate_chain(
        get_openai_chat_llm(model_name="gpt-3.5-turbo-0613"),
        input_keys=list(input.keys()),
        target_language="German",
    )
    print(chain.run(input=input))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_translate_standard():
    input = {
        "name": "OpenAI",
        "description": "OpenAI is an American artificial intelligence (AI) research laboratory.",
        "motive": 'Some scientists have articulated concerns.',
    }
    chain = create_translate_chain(
        Cohere(
            model="command-xlarge-beta",
            temperature=0.0,
            max_tokens=1024
        ),
        input_keys=list(input.keys()),
        target_language="German",
    )
    print(chain.run(json.dumps(input)))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_generic_standard():
    input = {
        "name": "OpenAI",
        "description": "OpenAI is an American artificial intelligence (AI) research laboratory.",
        "motive": 'Some scientists have articulated concerns about AI.',
    }
    chain = create_generic_chain(
        get_openai_chat_llm(model_name="gpt-3.5-turbo-0613"),
        # Cohere(
        #     model="command-xlarge-beta",
        #     temperature=0.0,
        #     max_tokens=1024
        # ),
        instructions="Compress the description into 3 words.",
        output_format={
            "reasoning": "the reasoning behind the result",
            "result": "the result of the task"
        }
    )
    print(chain.run(json.dumps(input)))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_compose():
    input = {
        "firstname": "Jim",
        "lastname": "Simpson",
        "question": 'Where is my order?',
        "customer_service_answer": 'no order',
    }
    chain = create_compose_chain(
        get_openai_chat_llm(model_name="gpt-3.5-turbo"),
        #Cohere(
        #    model="command-xlarge-beta",
        #    temperature=0.0,
        #    max_tokens=1024
        #),
        type="email",
        instructions_or_template="Hey { firstname} you little { nickname },\n{ thank the customer for his genius question and apologize}\nThank you, bye.",
        language="English",
        style="informal",
        tone="friendly",
        sender="My company",
        length="very brief"
    )
    print(chain.run(input=input))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_openapi():
    chain = get_openapi_chain("http://localhost:8090/v3/api-docs", verbose=True)
    print(chain.run("list some email addresses of customers (start at page 0)"))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_flare():
    loader = WebBaseLoader([
        "https://help.netflix.com/en/node/24926?ui_action=kb-article-popular-categories",
        "https://help.netflix.com/en/node/41049?ui_action=kb-article-popular-categories",
        "https://help.netflix.com/en/node/407"
    ])
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    chroma_retriever = Chroma.from_documents(texts, embeddings).as_retriever()

    flare = FlareChain.from_llm(
        get_openai_chat_llm(),
        retriever=chroma_retriever,
        max_generation_len=164,
        min_prob=0.3,
        verbose=True
    )

    print("\n\n")
    print(flare.run("what happens if an account is canceled that still has gift card balance?"))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_index_test_docs():
    loader = WebBaseLoader([
        "https://en.wikipedia.org/wiki/Trek_Bicycle_Corporation",
        "https://en.wikipedia.org/wiki/Electra_Bicycle_Company",
        "https://en.wikipedia.org/wiki/LeMond_Racing_Cycles"
    ])
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    Weaviate.from_documents(
        docs,
        embeddings,
        weaviate_url='http://localhost:8080/',
        index_name='Test_index',
        by_text=False
    )


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_create_skill_index():
    vs = get_vector_store(
        'weaviate',
        'http://localhost:8080/SkillLibrary',
        OpenAIEmbeddings(),
    )
    vs._client.schema.create_class({
        "class": 'SkillLibrary',
        "properties": [
            {
                "name": "text",
                "dataType": ["text"],
            },
            {
                "name": "task",
                "dataType": ["text"],
            },
            {
                "name": "comment",
                "dataType": ["text"],
            },
            {
                "name": "function",
                "dataType": ["text"],
            },
            {
                "name": "example_call",
                "dataType": ["text"],
            },
        ],
    })


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_clear_skills():
    vs = get_vector_store(
        'weaviate',
        'http://localhost:8080/SkillLibrary',
        OpenAIEmbeddings(),
        meta_attributes=['task', 'comment', 'function', 'example_call']
    )
    vs._client.schema.delete_class('SkillLibrary')


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_retrieve():
    embeddings = get_embeddings("openai", "text-embedding-ada-002")
    vector_store = get_vector_store(
        'azure_cognitive_search',
        os.getenv("AZURE_COGNITIVE_SEARCH_URL") + "/" + "bikestore",
        embeddings,
        password=os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
    )
    parent_document_store = get_document_store(
        "azure_cosmos_nosql",
        os.getenv("AZURE_COSMOS_DB_URL"),
        "bikestore",
        password=os.getenv("AZURE_COSMOS_DB_KEY")
    )
    summary_store = get_vector_store(
        'azure_cognitive_search',
        os.getenv("AZURE_COGNITIVE_SEARCH_URL") + "/" + "summary-index",
        embeddings,
        password=os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
    )

    qa = create_retrieval_agent(
        llm=ChatOpenAI(model_name="gpt-4", temperature=0),
        filter_llm=ChatOpenAI(model_name="gpt-4", temperature=0),
        vector_store=vector_store,
        multi_query_expansion=False,
        # metadata_field_info=[
        #     {
        #         "name": "bike_make",
        #         "description": "The bike make.",
        #         "type": "string",
        #         "enum": ["Sun Bicycles", "Cowboy"]
        #     },
        #     {
        #         "name": "bike_model",
        #         "description": "The bike model.",
        #         "type": "string",
        #         "enum": ["Electrolite", "3"]
        #     },
        # ],
        reranker="cohere",
        filter_metadata_field="bike_model",
        summary_store=summary_store,
        parent_document_store=parent_document_store,
    )
    print(qa(
            inputs={
                "input": "What is the weight limit of the Electra Townie Go?",
                "context": ""
            })["output"]["answer"])


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_flare_instruct():
    llm = get_openai_chat_llm(model_name='gpt-4')

    retriever = get_vector_store(
        'weaviate',
        'http://localhost:8080/Test_index',
        OpenAIEmbeddings()
    ).as_retriever()

    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
    )

    chain = FLAREInstructChain.from_llm(llm=llm, retriever=retriever, retrieval_qa=retrieval_qa)
    print(chain.run('What is the cancel policy? Specifically for the pro plan?'))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_code_eval():
    def get_accounts() -> List[Tuple[int, str, float]]:
        """Returns all accounts as a tuple (id, full name, balance)"""
        pass
    functions = [get_accounts]
    function_descriptions = get_python_functions_descriptions(functions)
    chain = create_code_eval_chain(
        llm=get_openai_chat_llm(model_name='gpt-4')
    )
    print(chain.run(
        task="Calculate the sum of all account balances",
        context="",
        function="""
def sum_account_balances():
    accounts = get_accounts()
    total_balance = sum(account[2] for account in accounts)
    return total_balance/2

sum_account_balances()
        """,
        functions=function_descriptions,
        result="3745.01"
    ))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_code_comment():
    chain = create_code_comment_chain(
        llm=get_openai_chat_llm(model_name='gpt-3.5-turbo')
    )
    print(chain.run(
        task="Calculate the sum of all account balances",
        function="""
def sum_account_balances():
    accounts = get_accounts()
    total_balance = sum(account[2] for account in accounts)
    return total_balance

sum_account_balances()
        """,
        result="3745.01"
    ))


# todo old agents
# def test_code_execution():
#     llm = get_openai_chat_llm(model_name='gpt-4')
#
#     def get_accounts() -> List[Tuple[int, str, float]]:
#         """Returns all accounts as a tuple (id, full name, balance)"""
#         return [
#             (1, "Max Power", 213.1),
#             (2, "Jeff Jefferson", 2343.3),
#             (3, "Heinz Wolff", 100.0),
#             (4, "Job Jeb", 98.11),
#             (5, "Max Mustermann", 990.5),
#         ]
#
#     chain = PythonCodeExecutionChain.from_llm_and_functions(
#         llm=llm,
#         functions=[get_accounts],
#         output_schema={"sum": "the sum of all accounts"}
#     )
#     print(chain.run(
#         context="",
#         input="Return the first account"
#     ))

# def test_database_code_execution():
#     llm = get_openai_chat_llm(model_name='gpt-4')
#     db = SQLDatabase(create_engine('postgresql://postgres:postgres@localhost:5438/postgres'))
#
#     agent = create_database_code_execution_agent(llm=llm, db=db)
#
#     print(agent.run(
#         context="customerName: Charolette Rice",
#         input="Find the phone number of the customer"
#     ))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_openapi_functions():
    spec = get_test_api_spec_str_for_url("http://localhost:8090")
    if isinstance(spec, str):
        for conversion in (
            OpenAPISpec.from_url,
            OpenAPISpec.from_file,
            OpenAPISpec.from_text,
        ):
            try:
                spec = conversion(spec)  # type: ignore[arg-type]
                break
            except Exception:  # noqa: E722
                pass
        if isinstance(spec, str):
            raise ValueError(f"Unable to parse spec from source {spec}")
    openai_fns, call_api_fn = openapi_spec_to_openai_fn(spec)
    #print(json.dumps(openai_fns, indent=2))
    print(call_api_fn("getcustomers", {"params": {"page": 0, "pageSize": 1}}).text)



