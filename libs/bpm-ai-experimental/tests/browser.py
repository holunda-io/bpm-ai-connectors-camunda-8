import asyncio

from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.voice.openai_voice import OpenAIVoice
from dotenv import load_dotenv

from bpm_ai_experimental.browser_agent.agent import run_browser_agent
from bpm_ai_experimental.browser_agent.util.browser import PlaywrightBrowser
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html, mark_interactive_dom
from bpm_ai_experimental.browser_agent.util.vision import run_vision_qa

load_dotenv(dotenv_path='../../../connector-secrets.txt')


async def run():
    browser = PlaywrightBrowser(headless=False)
    await browser.start("https://weblogin.cloud.camunda.io/")

    while True:
        #title, html = await get_simplified_html(browser)
        #print(html)
        await mark_interactive_dom(browser)
        input()
        print("#######################################################################################################")

asyncio.run(run())