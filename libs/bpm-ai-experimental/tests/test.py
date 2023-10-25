import asyncio

from bpm_ai_experimental.browser_agent.agent import run_browser_agent

print(
    print(asyncio.run(
        run_browser_agent("http://google.de", "")
    ))
)