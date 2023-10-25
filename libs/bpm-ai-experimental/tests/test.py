import asyncio

from dotenv import load_dotenv

from bpm_ai_experimental.browser_agent.agent import run_browser_agent
load_dotenv(dotenv_path='../../../connector-secrets.txt')


url = "https://hoang-bistro.de/"

asyncio.run(run_browser_agent(url, "Dismiss both the cookie and opening hours banners. Then add a Coke to the cart"))