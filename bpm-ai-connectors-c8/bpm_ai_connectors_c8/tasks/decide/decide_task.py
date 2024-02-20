from typing import Any

from bpm_ai.decide.decide import decide_llm, decide_classifier
from bpm_ai_core.classification.zero_shot_classifier import ZeroShotClassifier
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.ocr.ocr import OCR
from bpm_ai_core.speech_recognition.asr import ASRModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

decide_router = ZeebeTaskRouter()


@ai_task(decide_router, "decide", 2)
async def decide(
        llm: LLM | None,
        asr: ASRModel | None,
        ocr: OCR | None,
        input_json: dict,
        question: str,
        output_type: str,
        classifier: ZeroShotClassifier | None = None,
        possible_values: list[Any] | None = None,
        strategy: str | None = None
):
    if llm:
        return await decide_llm(
            llm=llm,
            asr=asr,
            ocr=ocr,
            input_data=input_json,
            instructions=question,
            output_type=output_type,
            possible_values=possible_values,
            strategy=strategy
        )
    else:
        return await decide_classifier(
            classifier=classifier,
            asr=asr,
            ocr=ocr,
            input_data=input_json,
            question=question,
            output_type=output_type,
            possible_values=possible_values,
        )
