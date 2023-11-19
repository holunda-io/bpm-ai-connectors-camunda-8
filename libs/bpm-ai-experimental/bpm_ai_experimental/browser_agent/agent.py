import asyncio
import json
import os
import time
from typing import List

from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ToolCallsMessage, ToolResultMessage, ChatMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable
from playwright.async_api import async_playwright, Playwright

from bpm_ai_experimental.browser_agent.util.browser import PlaywrightBrowser
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html, mark_interactive_dom
from bpm_ai_experimental.browser_agent.util.vision import run_vision_qa


@traceable(run_type="chain", name="BrowserAgent")
async def run_browser_agent(llm: LLM, start_url: str, input_data: dict, task: str, creds: dict | None = {}, output_schema: dict | None = None) -> dict:
    print("[start] run_browser_agent")
    browser = PlaywrightBrowser(headless=False)
    await browser.start(start_url)
    time.sleep(3)

    async def click(thought: str, elem_id: str):
        return await browser.click(elem_id)

    async def scroll(thought: str, down: bool):
        await browser.scroll(down)

    async def goto(thought: str, url: str):
        return await browser.goto(url)

    async def reload(thought: str):
        return await browser.reload()

    async def go_back(thought: str):
        return await browser.go_back()

    async def type_text(thought: str, elements: List[dict], submit: bool):
        for e in elements:
            if e["text"] in creds.keys():
                text = creds[e["text"]]
            else:
                text = e["text"]
            error = await browser.type_text(e["elem_id"], text)
            if error:
                return error
        if submit:
            await browser.enter()

    async def screenshot_analyse(thought: str, elem_id: str, question: str):
        await browser.screenshot(elem_id)
        return run_vision_qa("screenshot.png", question)

    browser_tools = [
        Tool.from_callable(
            "goto",
            "Navigates to the given url. Should usually only be used if explicitly asked by the user, otherwise navigate by clicking links where possible.",
            {"thought": "Always describe what to do and why", "url": "The url to navigate to"},
            goto
        ),
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
            "reload",
            "Reloads the current page",
            {"thought": "Always describe what to do and why"},
            reload
        ),
        Tool.from_callable(
            "go_back",
            "Navigate to the previous page in history",
            {"thought": "Always describe what to do and why"},
            reload
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
            "screenshot_analyse",
            "Uses a vision AI to answer a question about an element based on its actual rendered, (static) visual appearance. Useful if the textual DOM representation is not enough.",
            {
                "thought": "Always describe what to do and why",
                "elem_id": "The id of the element to look at",
                "question": "the question to answer about the element"},
            screenshot_analyse
        ),
        Tool.from_callable(
            "finish",
            "Finishes the task with a final result",
            output_schema if output_schema
            else {"result": "The result information the task asked for or TASK_COMPLETED if no result text needed"},
            lambda x: x
        )
    ]

    async def run_text_based():
        """
        Run text/html based agent.
        :return:
        """

        action_history = []
        did_retry = False
        while True:
            title, html = await get_simplified_html(browser)
            if not html:
                if did_retry:
                    raise Exception(f"Could not parse HTML for page {browser.page.url}")
                else:
                    time.sleep(2)
                    did_retry = True
                    print("[WARN] Retry parsing html")
                    continue
            else:
                did_retry = False

            for k, v in creds.items():
                if isinstance(html, str):
                    html = html.replace(v, k)

            # print()
            # print(html)
            # print()

            _input_data = input_data if not creds else input_data | {k: k for k, v in creds.items()}
            print(f"input data: {_input_data}")

            prompt = Prompt.from_file(
                "browser_agent",
                is_tool=lambda x: isinstance(x, ToolResultMessage),
                is_chat=lambda x: isinstance(x, ChatMessage),
                start_url=start_url,
                title=title,
                html=html,
                context=json.dumps(_input_data, indent=2),
                task=task,
                can_scroll_down=await browser.can_scroll_down(),
                can_scroll_up=await browser.can_scroll_up(),
                action_history=action_history
            )
            # print(prompt.format())

            # input()
            print("[Thinking...]")

            actions = llm.predict(prompt, tools=browser_tools)
            action_history.append(actions)

            if isinstance(actions, ToolCallsMessage):
                thought_key = "thought"
                print(
                    f"THOUGHT: {', '.join([t.payload_dict()[thought_key] if thought_key in t.payload_dict().keys() else '' for t in actions.tool_calls])}")
                print(
                    f"ACTIONS: {[f'{action.name}({str({k: v for k, v in action.payload_dict().items() if k != thought_key})})' for action in actions.tool_calls]}")

                for action in actions.tool_calls:
                    if action.name == "finish":
                        result = action.payload_dict()
                        print(f"FINAL_RESULT: {result}")
                        await browser.close()
                        return result
                    else:
                        result = await action.ainvoke()
                        time.sleep(1)  # todo

                    action_history.append(
                        ToolResultMessage(id=action.id, content=result)
                    )

            else:
                print("NO FUNCTION CALL!")
                print(actions.content)

            time.sleep(1)  # todo

    async def run_vision_based():
        """
        Run vision based agent.
        :return:
        """
        vision_llm = ChatOpenAI(model="gpt-4-vision-preview")

        action_history = []

        while True:
            title, html = await get_simplified_html(browser)
            #print(html)
            #await mark_interactive_dom(browser)
            await browser.screenshot()

            # print()
            # print(html)
            # print()

            _input_data = input_data if not creds else input_data | {k: k for k, v in creds.items()}
            print(f"input data: {_input_data}")

            vision_prompt = Prompt.from_file(
                "browser_vision_agent",
                start_url=start_url,
                context=json.dumps(_input_data, indent=2),
                task=task,
                html=html,
                can_scroll_down=await browser.can_scroll_down(),
                can_scroll_up=await browser.can_scroll_up(),
                action_history=action_history
            )

            result = vision_llm.predict(vision_prompt)
            print(result)

            prompt = Prompt.from_file(
                "browser_agent_executor",
                context=json.dumps(input_data, indent=2),
                task=task,
                actions=result
            )
            # print(prompt.format())

            input()
            print("[Thinking...]")

            actions = llm.predict(prompt, tools=browser_tools)
            action_history.append(actions)

            if isinstance(actions, ToolCallsMessage):
                thought_key = "thought"
                print(
                    f"THOUGHT: {', '.join([t.payload_dict()[thought_key] if thought_key in t.payload_dict().keys() else '' for t in actions.tool_calls])}")
                print(
                    f"ACTIONS: {[f'{action.name}({str({k: v for k, v in action.payload_dict().items() if k != thought_key})})' for action in actions.tool_calls]}")

                for action in actions.tool_calls:
                    if action.name == "finish":
                        result = action.payload_dict()
                        print(f"FINAL_RESULT: {result}")
                        await browser.close()
                        return result
                    else:
                        result = await action.ainvoke()
                        time.sleep(1)  # todo

                    action_history.append(
                        ToolResultMessage(id=action.id, content=result)
                    )

            else:
                print("NO FUNCTION CALL!")
                print(actions.content)

            time.sleep(1)  # todo

    return await run_vision_based()
