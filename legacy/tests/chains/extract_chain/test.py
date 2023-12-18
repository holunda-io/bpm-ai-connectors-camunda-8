from unittest.mock import Mock, patch
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from gpt.chains.extract_chain.chain import create_extract_chain


def test_create_extract_chain_openai():
    llm = Mock(spec=ChatOpenAI)
    output_schema = {'key1': 'value1', 'key2': 'value2'}
    repeated = False
    repeated_description = None

    with patch('gpt.chains.extract_chain.chain.create_openai_functions_extract_chain') as mock_openai_chain:
        chain = create_extract_chain(output_schema, llm, repeated, repeated_description)

        mock_openai_chain.assert_called_once_with(llm, output_schema, repeated, repeated_description or "")
        assert chain == mock_openai_chain.return_value


def test_create_extract_chain_standard():
    llm = Mock(spec=BaseLanguageModel)
    output_schema = {'key1': 'value1', 'key2': 'value2'}
    repeated = False
    repeated_description = None

    with patch('gpt.chains.extract_chain.chain.create_standard_extract_chain') as mock_standard_chain:
        chain = create_extract_chain(output_schema, llm, repeated, repeated_description)

        mock_standard_chain.assert_called_once_with(llm, output_schema, repeated)
        assert chain == mock_standard_chain.return_value
