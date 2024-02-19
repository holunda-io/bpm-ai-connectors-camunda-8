from bpm_ai.extract.extract import extract_llm, extract_qa
from bpm_ai_core.question_answering.question_answering import QuestionAnswering
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.ocr.ocr import OCR
from bpm_ai_core.speech_recognition.asr import ASRModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

extract_router = ZeebeTaskRouter()


@ai_task(extract_router, "extract", 2)
async def extract(
    llm: LLM | None,
    asr: ASRModel | None,
    ocr: OCR | None,
    input_json: dict,
    output_schema: dict,
    mode: str,
    entities_description="",
    qa: QuestionAnswering | None = None
):
    multiple = (mode == 'MULTIPLE')
    if llm:
        return await extract_llm(
            llm=llm,
            asr=asr,
            ocr=ocr,
            input_data=input_json,
            output_schema=output_schema,
            multiple=multiple,
            multiple_description=entities_description
        )
    else:
        return await extract_qa(
            qa=qa,
            asr=asr,
            ocr=ocr,
            input_data=input_json,
            output_schema=output_schema,
            multiple=multiple,
            multiple_description=entities_description
        )
