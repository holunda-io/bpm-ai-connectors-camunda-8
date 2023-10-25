import asyncio
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.template import format_prompt
from playwright.async_api import async_playwright, Playwright

from bpm_ai_experimental.browser_agent.util.browser import start_playwright, type_text, click
from bpm_ai_experimental.browser_agent.util.simplify_dom import get_simplified_html


async def run_browser_agent(start_url: str, task: str) -> str:
    llm = ChatOpenAI(model="gpt-4")

    playwright, browser, page = await start_playwright(start_url, headless=False)

    actions = []

    while True:
        title, html = await get_simplified_html(page)

        system_prompt = format_prompt("prompts/system")
        user_prompt = format_prompt(
            "prompts/user",
            title=title,
            html=html,
            task=task,
            action_history=str(actions)
        )

        print()
        print(user_prompt)
        print()

        input()

        action = llm.predict_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            output_schema={
                "last_action_complete": {"type": "boolean", "description": "Review the last step and verify that is was completed successfully and completely. If not, complete it now!"},
                "thoughts": {"type": "string", "description": "Describe your thoughts on what to do next, one thing at a time."},
                "id_to_click": {"type": "number"}
            }
        )
        actions.append(action)

        print(f"THOUGHT: {action['thoughts']}")
        print(f"ACTION:  click({action['id_to_click']})")

        await click(page, str(action['id_to_click']))

        #await type_text(page, id, text)

    await browser.close()
    await playwright.stop()

    return ""
