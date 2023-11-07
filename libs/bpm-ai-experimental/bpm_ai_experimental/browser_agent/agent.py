import asyncio
import json
import time
from typing import List

from bpm_ai_core.llm.common.function import Function
from bpm_ai_core.llm.common.message import FunctionCallMessage
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable
from playwright.async_api import async_playwright, Playwright

from bpm_ai_experimental.browser_agent.util.browser import PlaywrightBrowser
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html


@traceable(run_type="chain", name="BrowserAgent")
async def run_browser_agent(start_url: str, task: str) -> str:
    llm = ChatOpenAI(model="gpt-4")

    browser = PlaywrightBrowser(headless=False)
    await browser.start(start_url)

    async def click(elem_id: str):
        return await browser.click(elem_id)

    async def scroll(down: bool):
        return await browser.scroll(down)

    async def type_text(elements: List[dict], submit: bool): #elem_id: str, text: str, submit: bool
        for e in elements:
            await browser.type_text(e["elem_id"], e["text"])
        if submit:
            await browser.enter()

    async def visual_interpretation(elem_id: str, question: str):
        return await browser.screenshot(elem_id)

    action_history = []

    while True:
        title, html = await get_simplified_html(browser)
        html = (html[:5000] + '[...]') if len(html) > 5000 else html

        #print()
        #print(html)
        #print()

        prompt = Prompt.from_file(
            "browser_agent",
            title=title,
            html=html,
            task=task,
            can_scroll_down=await browser.can_scroll_down(),
            can_scroll_up=await browser.can_scroll_up(),
            action_history=action_history
        )

        input()
        print("[Thinking...]")

        action = llm.predict(
            prompt,
            functions=[
                Function.from_callable(
                    "click",
                    "Clicks on an element",
                    {"elem_id": "The id of the element"},
                    click
                ),
                Function.from_callable(
                    "scroll",
                    "Scrolls up or down by one viewport height",
                    {"down": {"type": "boolean", "description": "Whether to scroll down - otherwise scroll up"}},
                    scroll
                ),
                Function.from_callable(
                    "type_text",
                    "Types given text into an input elements",
                    {
                        "elements": {"type": "array", "description": "Elements to type text into",
                                     "items": {"elem_id": "The id of the element", "text": "The text to type"}},
                        "submit": {"type": "boolean", "description": "Whether to hit enter after typing the text"}
                    },
                    type_text
                ),
                Function.from_callable(
                    "visual_interpretation",
                    "Uses a vision AI to answer a question about an element based on its actual rendered, visual appearance. Useful if the textual DOM representation is not enough.",
                    {"elem_id": "The id of the element to look at", "question": "the question to answer about the element"},
                    visual_interpretation
                ),
                Function.from_callable(
                    "final_result",
                    "Finishes the task with a final result",
                    {"result": "The result information the task asked for or TASK_COMPLETED if no result text needed"},
                    type_text
                )
            ]
        )
        action_history.append(action)

        if isinstance(action, FunctionCallMessage):
            print(f"THOUGHT: {action.content}")
            print(f"ACTION: {action.name}({action.payload})")

            if action.name == "final_result":
                print(f"FINAL_RESULT:  {action.payload_dict()['result']}")
                break
            else:
                await action.ainvoke()

        else:
            print("NO FUNCTION CALL!")
            print(action.content)

        time.sleep(1)

        # await type_text(page, id, text)

    await browser.close()

    return ""
