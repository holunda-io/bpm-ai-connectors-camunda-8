import time
from typing import Tuple, Optional

from playwright.async_api import Playwright, async_playwright, Browser, Page

from bpm_ai_experimental.browser_agent.util.injection import ripple_css, ripple_js, disable_animations


class PlaywrightBrowser:
    def __init__(self, headless: bool = True):
        self.page: Optional[Page] = None
        self.browser = None
        self.playwright = None
        self.headless = headless

    async def prepare_page(self) -> Page:
        if not self.page:
            raise Exception("Browser not initialized, call start() first!")

        await self.page.wait_for_load_state('load')
        await self.page.wait_for_load_state('networkidle')

        if self.headless:
            await self.page.add_style_tag(content=disable_animations)

        await self.page.add_style_tag(content=ripple_css)
        await self.page.add_script_tag(content=ripple_js)

        return self.page

    async def start(self, url: str) -> Tuple[Playwright, Browser, Page]:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless
            # ignore_default_args=["--headless"],
            # args=["--headless=new"],
        )
        #context = await self.browser.new_context(viewport={'width': 1280, 'height': 1024})
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({'width': 1280, 'height': 1000})

        await self.page.goto(url)

        await self.prepare_page()

        return self.playwright, self.browser, self.page

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()

    async def click(self, elem_id: str):
        await self.page.get_by_test_id(elem_id).click()

    async def type_text(self, elem_id: str, text: str, submit: bool = False):
        await self.page.get_by_test_id(elem_id).clear()
        await self.page.get_by_test_id(elem_id).type(text, delay=25)
        if submit:
            await self.enter()

    async def enter(self):
        await self.page.keyboard.press("Enter")

    async def can_scroll_down(self):
        scroll_info = await self.get_scroll_info()
        return scroll_info["canScrollDown"]

    async def can_scroll_up(self):
        scroll_info = await self.get_scroll_info()
        return scroll_info["canScrollUp"]

    async def scroll(self, down: bool = True):
        scroll_info = await self.get_scroll_info()

        print(scroll_info)

        if down and scroll_info["canScrollDown"]:
            await self.page.mouse.wheel(0, scroll_info["viewportHeight"])
        elif not down and scroll_info["canScrollUp"]:
            await self.page.mouse.wheel(0, -scroll_info["viewportHeight"])

    async def get_scroll_info(self):
        return await self.page.evaluate("""() => ({
            canScrollDown: document.documentElement.scrollHeight > (window.innerHeight + window.scrollY),
            canScrollUp: window.scrollY > 0,
            documentHeight: document.documentElement.scrollHeight,
            viewportHeight: window.innerHeight,
            currentScrollPosition: window.scrollY
        })""")

    async def screenshot(self, elem_id: str):
        await self.page.get_by_test_id(elem_id).screenshot(path="screenshot.png")
