from unittest.mock import Mock, patch
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from gpt.chains.decide_chain.chain import create_decide_chain


def test_create_decide_chain_openai():
    llm = Mock(spec=ChatOpenAI)
    instructions = 'Decide this'
    output_type = 'string'
    possible_values = ['value1', 'value2']

    with patch('gpt.chains.decide_chain.chain.create_openai_functions_decide_chain') as mock_openai_chain:
        chain = create_decide_chain(llm, instructions, output_type, possible_values)

        mock_openai_chain.assert_called_once_with(llm, instructions, output_type, possible_values)
        assert chain == mock_openai_chain.return_value


def test_create_decide_chain_standard():
    llm = Mock(spec=BaseLanguageModel)
    instructions = 'Decide this'
    output_type = 'string'
    possible_values = ['value1', 'value2']

    with patch('gpt.chains.decide_chain.chain.create_standard_decide_chain') as mock_standard_chain:
        chain = create_decide_chain(llm, instructions, output_type, possible_values)

        mock_standard_chain.assert_called_once_with(llm, instructions, output_type, possible_values)
        assert chain == mock_standard_chain.return_value
