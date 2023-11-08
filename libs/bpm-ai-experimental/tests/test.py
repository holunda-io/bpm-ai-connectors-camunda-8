import asyncio

from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.voice.openai_voice import OpenAIVoice
from dotenv import load_dotenv

from bpm_ai_experimental.browser_agent.agent import run_browser_agent
load_dotenv(dotenv_path='../../../connector-secrets.txt')


#url = "https://hoang-bistro.de/produkt/cola-033l-122/"
#url = "https://hoang-bistro.de/"
url = "https://hoang-bistro.de/produkt-kategorie/alokoholfreie-getraenke/"
#url = "https://de.wikipedia.org/"

task = "Dismiss both the cookie and opening hours banners. Then add a Coke to the cart. Finally order for Max Mustermann."
#task = "Add a coke to the cart, but only if it is the special christmas can!"
#task = "Return a list of all available drinks with their prices."


print("What should I do?")

#voice = OpenAIVoice()
#task = voice.listen(language="de")
#print(task)

result = asyncio.run(run_browser_agent(url, task))

#voice.speak("Das Ergebnis ist: " + result)