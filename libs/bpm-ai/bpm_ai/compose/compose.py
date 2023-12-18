import re
from typing import TypedDict, Callable

from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable

from bpm_ai.common.json_utils import json_to_md
from bpm_ai.common.multimodal import prepare_audio
from bpm_ai.compose.util import remove_stop_words, type_to_prompt_type_str, decode_if_needed

TEMPLATE_VAR_PATTERN = r'\{\s*([^{}\s]+(?:\s*[^{}\s]+)*)\s*\}'


class TextProperties(TypedDict):
    style: str
    type: str
    tone: str
    length: str
    language: str
    temperature: str


@traceable(name="Compose")
def run_compose(
    llm: LLM,
    input_data: dict[str, str | dict],
    template: str,
    properties: TextProperties
) -> dict:
    def desc_to_var_name(desc: str):
        v = remove_stop_words(desc, separator='_')
        return re.sub(r'[^A-Za-z0-9_\'äöüÄÖÜß]+', '', v).lower()

    def format_vars(template: str, f: Callable[[str], str]):
        return re.sub(TEMPLATE_VAR_PATTERN, lambda m: f(m.group(1)), template)

    #input_data = prepare_images(input_data)  todo enable once GPT-4V is stable
    input_data = prepare_audio(input_data)

    # all variables found in the template
    template_vars = re.findall(TEMPLATE_VAR_PATTERN, template)
    # map of template variables that are not already in the input and need to be generated
    template_vars_to_generate_dict = {desc_to_var_name(desc): desc for desc in template_vars if
                                      desc not in input_data.keys()}
    # input variables that are not present in the template
    non_template_input_var_dict = {k: v for k, v in input_data.items() if k not in template_vars}

    if len(template_vars_to_generate_dict) > 0:
        tool = Tool.from_callable(
            "store_text",
            "Stores composed text parts for template variables.",
            args_schema=template_vars_to_generate_dict,
            callable=lambda **x: x
        )

        prompt = Prompt.from_file(
            "compose",
            context=json_to_md(non_template_input_var_dict),
            # remove template braces from variables that are already present in the input to not confuse the model what to generate
            # we do not resolve these variables here to avoid sending that data to the API
            template=format_vars(template, lambda v: v if v in input_data.keys() else '{' + v + '}'),
            type=type_to_prompt_type_str(properties.get("type", "letter")),
            style=properties.get("style", "formal"),
            tone=properties.get("tone", "friendly"),
            length=properties.get("length", "adequate"),
            lang=properties.get("language", "English")
        )

        result = llm.predict(prompt, tools=[tool])

        if isinstance(result, ToolCallsMessage):
            generated_vars = result.tool_calls[0].invoke()
            # fix for encoding error in new OpenAI models API
            generated_vars = {k: decode_if_needed(v) for k, v in generated_vars.items()}
        else:
            generated_vars = {}
    else:
        generated_vars = {}

    input_vars = {desc_to_var_name(k): v for k, v in input_data.items()}
    all_vars = generated_vars | input_vars

    # resolve all template variables using either input or generated values
    result = format_vars(template, lambda v: all_vars[desc_to_var_name(v)])

    return {"text": result}



