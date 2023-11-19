from bpm_ai_core.llm.openai_chat import ChatOpenAI

from bpm_ai.extract.extract import run_extract


def test_extract():
    result = run_extract(
        ChatOpenAI(
            model="gpt-4-1106-preview"
        ),
        {"email": "Hey ich bins, der Meier John. Mein 30. Geburtstag war krass!"},
        output_schema={
            "firstname": "the firstname",
            "lastname": "the lastname",
            "age": {"type": "integer", "description": "age in years"},
            "language": "the language the email is written in, as two-letter ISO code"
        }
    )
    print(result)


def test_extract_repeated():
    result = run_extract(
        ChatOpenAI(
            model="gpt-4-1106-preview"
        ),
        {"email": "Hey ich wollte nur sagen, John, Mike und Sepp kommen alle mit! Ich kann leider nicht. Grüße, Maria"},
        output_schema={
            "firstname": "the firstname",
        },
        repeated=True,
        repeated_description="Only people that are coming"
    )
    print(result)


def test_extract_image():
    result = run_extract(
        ChatOpenAI(
            model="gpt-4-vision-preview"
        ),
        {
            "email": "Hey ich bins, der Meier John. Mein 30. Geburtstag war krass! Wetter war auch ok!",
            "photo": "/Users/bennet/Desktop/Screenshot 2023-10-16 at 00.13.54.png"
        },
        output_schema={
            "firstname": "the firstname",
            "lastname": "the lastname",
            "age": {"type": "integer", "description": "age in years"},
            "language": "the language the email is written in, as two-letter ISO code",
            "weather_conditions": "the weather conditions"
        }
    )
    print(result)

def test_extract_audio():
    result = run_extract(
        ChatOpenAI(
            #model="gpt-4"
        ),
        {
            "email": "Hey ich bins, der Meier John. Mein 30. Geburtstag war krass! Wetter war auch ok!",
            "voice_memo": "/Users/bennet/Downloads/speech2.m4a"
        },
        output_schema={
            "firstname": "the firstname",
            "lastname": "the lastname",
            "age": {"type": "integer", "description": "age in years"},
            "language": "the language the email is written in, as two-letter ISO code",
            "supercharger_price": {"type": "integer", "description": "the supercharger price in cent per kilowatt hour"}
        }
    )
    print(result)