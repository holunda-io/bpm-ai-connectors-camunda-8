from bpm_ai_core.classification.transformers_classifier import TransformersClassifier
from bpm_ai_core.classification.zero_shot_classifier import ZeroShotClassifier
from bpm_ai_core.question_answering.question_answering import QuestionAnswering
from bpm_ai_core.question_answering.transformers_qa import TransformersExtractiveQA
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.ocr.ocr import OCR
from bpm_ai_core.ocr.tesseract import TesseractOCR
from bpm_ai_core.speech_recognition.asr import ASRModel
from bpm_ai_core.speech_recognition.faster_whisper import FasterWhisperASR
from bpm_ai_core.speech_recognition.openai_whisper import OpenAIWhisperASR
from bpm_ai_core.translation.easy_nmt.easy_nmt import EasyNMT
from bpm_ai_core.translation.nmt import NMTModel

# job variable names that define custom models (as opposed to pre-configured in the element templates)
CUSTOM_MODEL_VARS = ["custom_asr", "custom_classifier", "custom_qa", "custom_nmt"]


def model_ids_to_models(kwargs: dict):
    if "llm" in kwargs.keys():
        kwargs["llm"] = model_id_to_llm(kwargs["llm"])
    if "ocr" in kwargs.keys():
        kwargs["ocr"] = model_id_to_ocr(kwargs.get("custom_ocr", kwargs["ocr"]))
    if "asr" in kwargs.keys():
        kwargs["asr"] = model_id_to_asr(kwargs.get("custom_asr", kwargs["asr"]))
    if "classifier" in kwargs.keys():
        kwargs["classifier"] = model_id_to_classifier(kwargs.get("custom_classifier", kwargs["classifier"]))
    if "qa" in kwargs.keys():
        kwargs["qa"] = model_id_to_qa(kwargs.get("custom_qa", kwargs["qa"]))
    if "nmt" in kwargs.keys():
        kwargs["nmt"] = model_id_to_nmt(kwargs.get("custom_nmt", kwargs["nmt"]))
    return kwargs


def model_id_to_llm(
    model_id: str
) -> LLM | None:
    if model_id.startswith("gpt"):
        return ChatOpenAI(model=model_id)
    else:
        return None


def model_id_to_ocr(
    model_id: str
) -> OCR | None:
    if model_id == "tesseract":
        return TesseractOCR()
    else:
        return None


def model_id_to_asr(
    model_id: str
) -> ASRModel | None:
    if model_id.startswith("openai"):
        return OpenAIWhisperASR(whisper_model=model_id.split('-', 1)[-1])
    elif model_id.startswith("faster_whisper"):
        return FasterWhisperASR(model_size=model_id.split('-', 1)[-1])
    else:
        return None


def model_id_to_classifier(
    model_id: str
) -> ZeroShotClassifier | None:
    return TransformersClassifier(model=model_id)


def model_id_to_qa(
    model_id: str
) -> QuestionAnswering | None:
    if '/' in model_id:
        return TransformersExtractiveQA(model=model_id)
    else:
        return None


def model_id_to_nmt(
    model_id: str
) -> NMTModel | None:
    if model_id.startswith('Helsinki-NLP/opus-mt'):
        return EasyNMT()
    else:
        return None
