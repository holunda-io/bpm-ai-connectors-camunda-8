from dotenv import load_dotenv

from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt

load_dotenv(dotenv_path='../../../connector-secrets.txt')

llm = ChatOpenAI()
prompt = Prompt.from_file("test", name="John", x=False)
print("Prompt: ")
print(prompt.format(llm_name="openai"))
print("Answer: ")
message = llm.predict(prompt)
print(message)