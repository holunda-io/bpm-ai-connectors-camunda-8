import pytest
from unittest.mock import Mock, patch
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from gpt.chains.translate_chain.chain import create_translate_chain


def test_create_translate_chain_openai():
    llm = Mock(spec=ChatOpenAI)
    input_keys = ['key1', 'key2']
    target_language = 'French'

    with patch('gpt.chains.translate_chain.chain.create_openai_functions_translate_chain') as mock_openai_chain:
        chain = create_translate_chain(llm, input_keys, target_language)

        mock_openai_chain.assert_called_once_with(llm, input_keys, target_language)
        assert chain == mock_openai_chain.return_value


def test_create_translate_chain_standard():
    llm = Mock(spec=BaseLanguageModel)
    input_keys = ['key1', 'key2']
    target_language = 'French'

    with patch('gpt.chains.translate_chain.chain.create_standard_translate_chain') as mock_standard_chain:
        chain = create_translate_chain(llm, input_keys, target_language)

        mock_standard_chain.assert_called_once_with(llm, input_keys, target_language)
        assert chain == mock_standard_chain.return_value
