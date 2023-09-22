from unittest.mock import Mock, patch
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from gpt.chains.compose_chain.chain import create_compose_chain


def test_create_compose_chain_template_openai():
    llm = Mock(spec=ChatOpenAI)
    instructions_or_template = 'Compose this {template}'
    type = 'letter'
    style = 'formal'
    tone = 'neutral'
    length = 'short'
    language = 'French'
    sender = None
    constitutional_principle = None

    with patch('gpt.chains.compose_chain.chain.TemplateComposeChain') as mock_template_chain:
        chain = create_compose_chain(llm, instructions_or_template, type, style, tone, length, language, sender, constitutional_principle)

        mock_template_chain.assert_called_once_with(llm=llm, template=instructions_or_template, type=type, language=language, style=style, tone=tone, length=length)
        assert chain == mock_template_chain.return_value


def test_create_compose_chain_no_template_openai():
    llm = Mock(spec=ChatOpenAI)
    instructions_or_template = 'Compose this'
    type = 'str'
    style = 'formal'
    tone = 'neutral'
    length = 'short'
    language = 'French'
    sender = "Sender"
    constitutional_principle = None

    with patch('gpt.chains.compose_chain.chain.create_standard_compose_chain') as mock_template_chain:
        chain = create_compose_chain(llm, instructions_or_template, type, style, tone, length, language, sender, constitutional_principle)

        mock_template_chain.assert_called_once_with(llm=llm, instructions=instructions_or_template, type=type, style=style, tone=tone, length=length, language=language, sender=sender, constitutional_principle=constitutional_principle)
        assert chain == mock_template_chain.return_value


def test_create_compose_chain_standard():
    llm = Mock(spec=BaseLanguageModel)
    instructions_or_template = 'Compose this'
    type = 'str'
    style = 'formal'
    tone = 'neutral'
    length = 'short'
    language = 'French'
    sender = "Sender"
    constitutional_principle = None

    with patch('gpt.chains.compose_chain.chain.create_standard_compose_chain') as mock_standard_chain:
        chain = create_compose_chain(llm, instructions_or_template, type, style, tone, length, language, sender, constitutional_principle)

        mock_standard_chain.assert_called_once_with(llm=llm, instructions=instructions_or_template, type=type, style=style, tone=tone, length=length, language=language, sender=sender, constitutional_principle=constitutional_principle)
        assert chain == mock_standard_chain.return_value
