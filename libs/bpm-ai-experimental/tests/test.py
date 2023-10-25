import asyncio

from bpm_ai_experimental.browser_agent.agent import run_browser_agent

url = "https://hoang-bistro.de/produkt-kategorie/alokoholfreie-getraenke/"

asyncio.run(run_browser_agent(url, ""))