import asyncio
import json
import time
from typing import List

from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable
from playwright.async_api import async_playwright, Playwright

from bpm_ai_experimental.browser_agent.util.browser import PlaywrightBrowser
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html


@traceable(run_type="chain", name="BrowserAgent")
async def run_browser_agent(start_url: str, task: str) -> str:
    llm = ChatOpenAI(model="gpt-4-1106-preview")

    browser = PlaywrightBrowser(headless=False)
    await browser.start(start_url)

    async def click(elem_id: str):
        await browser.click(elem_id)

    async def scroll(down: bool):
        await browser.scroll(down)

    async def type_text(elements: List[dict], submit: bool):
        for e in elements:
            await browser.type_text(e["elem_id"], e["text"])
        if submit:
            await browser.enter()

    async def visual_interpretation(elem_id: str, question: str):
        return await browser.screenshot(elem_id)

    browser_tools = [
        Tool.from_callable(
            "click",
            "Clicks on an element",
            {"elem_id": "The id of the element"},
            click
        ),
        Tool.from_callable(
            "scroll",
            "Scrolls up or down by one viewport height",
            {"down": {"type": "boolean", "description": "Whether to scroll down - otherwise scroll up"}},
            scroll
        ),
        Tool.from_callable(
            "type_text",
            "Types given text into an input elements",
            {
                "elements": {"type": "array", "description": "Elements to type text into",
                             "items": {"elem_id": "The id of the element", "text": "The text to type"}},
                "submit": {"type": "boolean", "description": "Whether to hit enter after typing the text"}
            },
            type_text
        ),
        Tool.from_callable(
            "visual_interpretation",
            "Uses a vision AI to answer a question about an element based on its actual rendered, visual appearance. Useful if the textual DOM representation is not enough.",
            {"elem_id": "The id of the element to look at", "question": "the question to answer about the element"},
            visual_interpretation
        ),
        Tool.from_callable(
            "final_result",
            "Finishes the task with a final result",
            {"result": "The result information the task asked for or TASK_COMPLETED if no result text needed"},
            type_text
        )
    ]

    action_history = []
    while True:
        title, html = await get_simplified_html(browser)

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
        print(prompt.format())

        #input()
        print("[Thinking...]")

        actions = llm.predict(prompt, tools=browser_tools)
        action_history.append(actions)

        if isinstance(actions, ToolCallsMessage):
            print(f"THOUGHT: {actions.content}")
            print(f"ACTIONS: {[f'{action.name}({action.payload})' for action in actions.tool_calls]}")

            for action in actions.tool_calls:
                if action.name == "final_result":
                    result = action.payload_dict()['result']
                    print(f"FINAL_RESULT: {result}")
                    await browser.close()
                    return result
                else:
                    await action.ainvoke()
                    time.sleep(0.5)  # todo

        else:
            print("NO FUNCTION CALL!")
            print(actions.content)

        time.sleep(1)  # todo

