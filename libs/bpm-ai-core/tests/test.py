from bpm_ai_core.llm.openai_chat import ChatOpenAI


def test_openai():
    llm = ChatOpenAI()
    res = llm.predict_text("Hello, beautiful day right?")
    print(res)


def test_openai_message():
    llm = ChatOpenAI()
    res = llm.predict_message([{"role": "user", "content": "Hello, beautiful day right?"}])
    print(res)


def test_openai_json():
    llm = ChatOpenAI()
    res = llm.predict_json(
        messages=[{"role": "user", "content": "Where is Hamburg?"}],
        output_schema={
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "continent": {"type": "string"},
            },
            "required": ["country", "continent"],
        }
    )
    print(res)


def test_openai_json_2():
    llm = ChatOpenAI()
    res = llm.predict_json(
        messages=[{"role": "user", "content": "How many Bundesländer are there?"}],
        output_schema={
            "länder": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    )
    print(res)
