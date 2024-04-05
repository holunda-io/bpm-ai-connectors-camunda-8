from bpm_ai.extract.extract import extract_llm, extract_qa
from bpm_ai_core.question_answering.question_answering import QuestionAnswering
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.ocr.ocr import OCR
from bpm_ai_core.speech_recognition.asr import ASRModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task
from bpm_ai_connectors_c8.models import remote_model

extract_router = ZeebeTaskRouter()


@ai_task(extract_router, "extract", 2)
async def extract(
    llm: LLM | None,
    input_json: dict,
    output_schema: dict,
    mode: str,
    entities_description="",
    asr: ASRModel | None = None,
    ocr: OCR | None = None,
    qa: QuestionAnswering | None = None,
    vqa: QuestionAnswering | None = None
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
            vqa=vqa,
            classifier=remote_model("TransformersClassifier"),  # non-configurable right now
            token_classifier=remote_model("TransformersTokenClassifier"),  # non-configurable right now
            asr=asr,
            ocr=ocr,
            input_data=input_json,
            output_schema=output_schema,
            multiple=multiple,
            multiple_description=entities_description
        )
