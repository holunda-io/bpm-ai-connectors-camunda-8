from unittest.mock import Mock, patch
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from gpt.chains.generic_chain.chain import create_generic_chain


def test_create_generic_chain_openai():
    llm = Mock(spec=ChatOpenAI)
    instructions = 'Perform a task'
    output_format = {'key1': 'value1', 'key2': 'value2'}

    with patch('gpt.chains.generic_chain.chain.create_openai_functions_generic_chain') as mock_openai_chain:
        chain = create_generic_chain(llm, instructions, output_format)

        mock_openai_chain.assert_called_once_with(llm, instructions, output_format)
        assert chain == mock_openai_chain.return_value


def test_create_generic_chain_standard():
    llm = Mock(spec=BaseLanguageModel)
    instructions = 'Perform a task'
    output_format = {'key1': 'value1', 'key2': 'value2'}

    with patch('gpt.chains.generic_chain.chain.create_standard_generic_chain') as mock_standard_chain:
        chain = create_generic_chain(llm, instructions, output_format)

        mock_standard_chain.assert_called_once_with(llm, instructions, output_format)
        assert chain == mock_standard_chain.return_value
        