import asyncio

from bpm_ai_core.llm.common.message import ToolResultMessage, ChatMessage, ToolCallsMessage, SingleToolCallMessage
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.voice.openai_voice import OpenAIVoice
from dotenv import load_dotenv

from bpm_ai_experimental.browser_agent.agent import run_browser_agent
from bpm_ai_experimental.browser_agent.util.vision import run_vision_qa

load_dotenv(dotenv_path='../../../connector-secrets.txt')


def get_tts_answer(q: str, raw_answer: str) -> str:
    prompt = Prompt.from_file("final_qa", question=q, answer=raw_answer)
    return ChatOpenAI().predict(prompt).content

#url = "https://www.tierheim-kiel.de/hunde/hunde-suchen-ein-zuhause-huendin.html"
#url = "https://hoang-bistro.de/produkt/cola-033l-122/"
url = "https://hoang-bistro.de/"
url = "https://green-stone-027bc5603.3.azurestaticapps.net"
url = "https://weblogin.cloud.camunda.io"
#url = "https://martinfowler.com/articles/2023-liberal-arts.html"
#url = "https://twitter.com/home"
#url="https://www.hamburger-tierschutzverein.de/tiervermittlung/hunde/grosse-hunde"
#url = "https://hoang-bistro.de/produkt-kategorie/alokoholfreie-getraenke/"
#url = "https://de.wikipedia.org/"

#task="Find the first dog that has its tongue out and return his name."
#task = "Add a large Coke and a small Sprite to the cart. Finally order for Max Mustermann."
#task = "Add a coke to the cart, but only if it is the special christmas can!"
#task = "Return a list of all available drinks with their prices."


#print("What should I do?")

voice = OpenAIVoice()
#task = "log in, switch the organisation to Holisticon, open the Tasklist component, and start a new Process_0o5b5xm process instance." does not find the components menu
task = "log in (submit by clicking, not enter), switch the organisation to Holisticon, open the Tasklist component via the Camunda components button, and start a new Process_0o5b5xm process instance."#voice.listen()
#task = "Log in and post a snippy retweet/repost in response to the first Tesla-themed post you find."#voice.listen()
#task = "From when is this blog post and who is the author?"
#task = "Select the battery issue example and submit for bennet.krause@gmail.com"
#print(task)



result = asyncio.run(run_browser_agent(
    ChatOpenAI(model="gpt-4-1106-preview"),
    url,
    input_data={},
    task=task,
    #output_schema={"autor": "the author name", "date": "the date"}
    creds={"username": "bennet.krause@holisticon.de", "password": "Bennet_987!Camunda"},
))

#tts_text = get_tts_answer(task, result)
#print(tts_text)

#voice.speak(tts_text)
