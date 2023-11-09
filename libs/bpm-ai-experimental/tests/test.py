import asyncio

from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.voice.openai_voice import OpenAIVoice
from dotenv import load_dotenv

from bpm_ai_experimental.browser_agent.agent import run_browser_agent
from bpm_ai_experimental.browser_agent.util.vision import run_vision_qa

load_dotenv(dotenv_path='../../../connector-secrets.txt')


#url = "https://hoang-bistro.de/produkt/cola-033l-122/"
#url = "https://hoang-bistro.de/"
url="https://www.hamburger-tierschutzverein.de/tiervermittlung/hunde/grosse-hunde"
#url = "https://hoang-bistro.de/produkt-kategorie/alokoholfreie-getraenke/"
#url = "https://de.wikipedia.org/"

task="Find the first dog that has its tongue out and return his name."
#task = "Add a large Coke and a small Sprite to the cart. Finally order for Max Mustermann."
#task = "Add a coke to the cart, but only if it is the special christmas can!"
#task = "Return a list of all available drinks with their prices."


#print("What should I do?")

#voice = OpenAIVoice()
#task = voice.listen(language="de")
#print(task)

result = asyncio.run(run_browser_agent(url, task))

#voice.speak("Das Ergebnis ist: " + result)

#print(run_vision_qa("screenshot.png", "Is that a dog?"))