import asyncio
from typing import Coroutine, Any, T

from bpm_ai_core.llm.openai_chat import ChatOpenAI
from playwright.async_api import async_playwright, Playwright


async def run_browser_agent(start_url: str, task: str) -> str:
    playwright: Playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False
        #ignore_default_args=["--headless"],
        #args=["--headless=new"],
    )

    page = await browser.new_page()
    res = await page.goto(start_url)

    return await res.text()
