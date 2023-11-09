from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt


def run_vision_qa(image_path: str, question: str) -> str:
    llm = ChatOpenAI(model="gpt-4-vision-preview")
    prompt = Prompt.from_file(
        "vision_qa",
        image_path=image_path,
        question=question
    )

    print("[Interpreting image...]")

    completion = llm.predict(prompt)
    print(completion)
    return completion.content