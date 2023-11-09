import asyncio
import json
import time
from typing import List

from bpm_ai_core.llm.common.message import ToolCallsMessage, ToolResultMessage, ChatMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable
from playwright.async_api import async_playwright, Playwright

from bpm_ai_experimental.browser_agent.util.browser import PlaywrightBrowser
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html
from bpm_ai_experimental.browser_agent.util.vision import run_vision_qa


@traceable(run_type="chain", name="BrowserAgent")
async def run_browser_agent(start_url: str, task: str) -> str:
    llm = ChatOpenAI(model="gpt-4-1106-preview")

    browser = PlaywrightBrowser(headless=False)
    await browser.start(start_url)

    async def click(thought: str, elem_id: str):
        await browser.click(elem_id)

    async def scroll(thought: str, down: bool):
        await browser.scroll(down)

    async def type_text(thought: str, elements: List[dict], submit: bool):
        for e in elements:
            await browser.type_text(e["elem_id"], e["text"])
        if submit:
            await browser.enter()

    async def visual_interpretation(thought: str, elem_id: str, question: str):
        await browser.screenshot(elem_id)
        return run_vision_qa("screenshot.png", question)

    browser_tools = [
        Tool.from_callable(
            "click",
            "Clicks on an element",
            {"thought": "Always describe what to do and why", "elem_id": "The id of the element"},
            click
        ),
        Tool.from_callable(
            "scroll",
            "Scrolls up or down by one viewport height",
            {"thought": "Always describe what to do and why", "down": {"type": "boolean", "description": "Whether to scroll down - otherwise scroll up"}},
            scroll
        ),
        Tool.from_callable(
            "type_text",
            "Types given text into an input elements",
            {
                "thought": "Always describe what to do and why",
                "elements": {"type": "array", "description": "Elements to type text into",
                             "items": {"elem_id": "The id of the element", "text": "The text to type"}},
                "submit": {"type": "boolean", "description": "Whether to hit enter after typing the text"}
            },
            type_text
        ),
        Tool.from_callable(
            "visual_interpretation",
            "Uses a vision AI to answer a question about an element based on its actual rendered, visual appearance. Useful if the textual DOM representation is not enough.",
            {
                "thought": "Always describe what to do and why",
                "elem_id": "The id of the element to look at",
                "question": "the question to answer about the element"},
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
            "browser_agent2",
            is_tool=lambda x: isinstance(x, ToolResultMessage),
            is_chat=lambda x: isinstance(x, ChatMessage),
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
            thought_key = "thought"
            print(f"THOUGHT: {', '.join([t.payload_dict()[thought_key] if thought_key in t.payload_dict().keys() else '' for t in actions.tool_calls])}")
            print(f"ACTIONS: {[f'{action.name}({str({k: v for k, v in action.payload_dict().items() if k != thought_key})})' for action in actions.tool_calls]}")

            for action in actions.tool_calls:
                if action.name == "final_result":
                    result = action.payload_dict()['result']
                    print(f"FINAL_RESULT: {result}")
                    await browser.close()
                    return result
                else:
                    result = await action.ainvoke()
                    time.sleep(0.5)  # todo

                action_history.append(
                    ToolResultMessage(id=action.id, content=result)
                )

        else:
            print("NO FUNCTION CALL!")
            print(actions.content)

        time.sleep(1)  # todo

