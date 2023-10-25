from typing import Tuple

from playwright.async_api import Playwright, async_playwright, Browser, Page


async def start_playwright(url: str, headless: bool = True) -> Tuple[Playwright, Browser, Page]:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=headless
        # ignore_default_args=["--headless"],
        # args=["--headless=new"],
    )
    page = await browser.new_page()
    await page.goto(url)
    await page.add_style_tag(
        content="*, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }"
    )
    return playwright, browser, page


async def click(page: Page, elem_id: str):
    await page.get_by_test_id(elem_id).click()


async def type_text(page: Page, elem_id: str, text: str):
    await page.get_by_test_id(elem_id).clear()
    await page.get_by_test_id(elem_id).type(text, delay=25)
