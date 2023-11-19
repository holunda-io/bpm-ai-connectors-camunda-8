import time
from typing import Tuple, Optional, Union

from playwright.async_api import Playwright, async_playwright, Browser, Page, Locator

from bpm_ai_experimental.browser_agent.util.injection import ripple_css, ripple_js, disable_animations


class PlaywrightBrowser:
    def __init__(self, headless: bool = True):
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.playwright: Optional[Playwright] = None
        self.headless = headless

    async def prepare_page(self) -> Page:
        if not self.page:
            raise Exception("Browser not initialized, call start() first!")

        await self.page.wait_for_load_state('load')
        #await self.page.wait_for_load_state('networkidle')

        try:
            if self.headless:
                await self.page.add_style_tag(content=disable_animations)

            await self.page.add_style_tag(content=ripple_css)
            await self.page.add_script_tag(content=ripple_js)
        except Exception:
            print("[WARNING] Could not add style or script tags to page.")

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
        await self.page.set_viewport_size({'width': 1100, 'height': 1000})

        await self.page.goto(url)

        await self.prepare_page()

        return self.playwright, self.browser, self.page

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()

    async def click(self, elem_id: str):
        try:
            await self.page.get_by_test_id(elem_id).click(timeout=5000)
        except Exception:
            return self.error_msg(elem_id, "click on")

    async def type_text(self, elem_id: str, text: str, submit: bool = False):
        try:
            await self.page.get_by_test_id(elem_id).clear(timeout=5000)
            await self.page.get_by_test_id(elem_id).type(text, delay=25)
            if submit:
                await self.enter()
        except Exception:
            return self.error_msg(elem_id, "type text in")

    def error_msg(self, elem_id, msg):
        return f"Could not {msg} element with id {elem_id}, maybe it is blocked by another element (dialog, banner, etc.) or not fully within the viewport (check if it is near the edge of the DOM and maybe try scolling first). Otherwise check if the id is correct."

    async def enter(self):
        await self.page.keyboard.press("Enter")

    async def reload(self):
        await self.page.reload(timeout=5000)

    async def go_back(self):
        await self.page.go_back(timeout=5000)

    async def goto(self, url: str):
        await self.page.goto(url, timeout=7500)

    async def can_scroll_down(self):
        scroll_info = await self.get_scroll_info()
        return scroll_info["canScrollDown"]

    async def can_scroll_up(self):
        scroll_info = await self.get_scroll_info()
        return scroll_info["canScrollUp"]

    async def scroll(self, down: bool = True):
        scroll_info = await self.get_scroll_info()
        if down and scroll_info["canScrollDown"]:
            await self.page.mouse.wheel(0, scroll_info["viewportHeight"] * 0.9)
        elif not down and scroll_info["canScrollUp"]:
            await self.page.mouse.wheel(0, -scroll_info["viewportHeight"] * 0.9)

    async def get_scroll_info(self):
        return await self.page.evaluate("""() => ({
            canScrollDown: document.documentElement.scrollHeight > (window.innerHeight + window.scrollY),
            canScrollUp: window.scrollY > 0,
            documentHeight: document.documentElement.scrollHeight,
            viewportHeight: window.innerHeight,
            currentScrollPosition: window.scrollY
        })""")

    async def screenshot(self, elem_id: str | None = None):
        try:
            if elem_id:
                elem = self.page.get_by_test_id(elem_id)
            else:
                elem = self.page
            await elem.screenshot(
                path="screenshot.png",
                timeout=5000
            )
        except Exception:
            return self.error_msg(elem_id, "screenshot")
