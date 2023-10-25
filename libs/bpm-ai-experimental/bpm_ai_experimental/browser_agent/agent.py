import asyncio
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from playwright.async_api import async_playwright, Playwright

from bpm_ai_experimental.browser_agent.util.browser import start_playwright, type_text, click
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html


async def run_browser_agent(start_url: str, task: str) -> str:

    playwright, browser, page = await start_playwright(start_url, headless=False)

    while True:
        title, html = await get_simplified_html(page)

        print(html)

        cmd = input()
        if ':' in cmd:
            id = cmd.split(':')[0]
            text = cmd.split(':')[-1]
            await type_text(page, id, text)
        else:
            id = cmd
            await click(page, id)

    await browser.close()
    await playwright.stop()

    return ""
