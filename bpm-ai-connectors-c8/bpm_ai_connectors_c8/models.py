import os
from typing import Any

from bpm_ai_core.classification.zero_shot_classifier import ZeroShotClassifier
from bpm_ai_core.llm.anthropic_chat.anthropic_chat import ChatAnthropic
from bpm_ai_core.llm.openai_chat.openai_chat import ChatOpenAI
from bpm_ai_core.ocr.amazon_textract import AmazonTextractOCR
from bpm_ai_core.ocr.azure_doc_intelligence import AzureOCR
from bpm_ai_core.question_answering.amazon_textract_docvqa import AmazonTextractDocVQA
from bpm_ai_core.question_answering.azure_doc_intelligence_docvqa import AzureDocVQA
from bpm_ai_core.question_answering.question_answering import QuestionAnswering
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.ocr.ocr import OCR
from bpm_ai_core.speech_recognition.asr import ASRModel
from bpm_ai_core.speech_recognition.openai_whisper import OpenAIWhisperASR
from bpm_ai_core.translation.amazon_translate import AmazonTranslate
from bpm_ai_core.translation.azure_translation import AzureTranslation
from bpm_ai_core.translation.nmt import NMTModel
from bpm_ai_core.util.remote_object import remote_object

# job variable names that define model parameters that should not be injected into the task function
# (instead only the final constructed model object is injected)
EXTRA_VARS = ["custom_asr", "custom_classifier", "custom_qa", "custom_vqa", "custom_nmt", "model_endpoint"]


def model_ids_to_models(kwargs: dict):
    if "llm" in kwargs.keys():
        kwargs["llm"] = model_id_to_llm(kwargs["llm"], kwargs)
    if "ocr" in kwargs.keys():
        kwargs["ocr"] = model_id_to_ocr(kwargs.get("custom_ocr", kwargs["ocr"]))
    if "asr" in kwargs.keys():
        kwargs["asr"] = model_id_to_asr(kwargs.get("custom_asr", kwargs["asr"]))
    if "classifier" in kwargs.keys():
        kwargs["classifier"] = model_id_to_classifier(kwargs.get("custom_classifier", kwargs["classifier"]))
    if "qa" in kwargs.keys():
        kwargs["qa"] = model_id_to_qa(kwargs.get("custom_qa", kwargs["qa"]))
    if "vqa" in kwargs.keys():
        kwargs["vqa"] = model_id_to_vqa(kwargs.get("custom_vqa", kwargs["vqa"]))
    if "nmt" in kwargs.keys():
        kwargs["nmt"] = model_id_to_nmt(kwargs.get("custom_nmt", kwargs["nmt"]))
    return kwargs


def model_id_to_llm(
    model_id: str,
    kwargs: dict
) -> LLM | None:
    if model_id.startswith("gpt"):
        return ChatOpenAI.for_openai(model=model_id)
    elif model_id == "azure-openai":
        return ChatOpenAI.for_azure(endpoint=kwargs["model_endpoint"])
    elif model_id == "openai-compatible":
        return ChatOpenAI.for_openai_compatible(endpoint=kwargs["model_endpoint"])
    elif model_id.startswith("claude"):
        return ChatAnthropic.for_anthropic(model=model_id)
    else:
        return None


def model_id_to_ocr(
    model_id: str
) -> OCR | None:
    if model_id == "tesseract":
        return remote_model("TesseractOCR")
    elif model_id == "amazon-textract":
        return AmazonTextractOCR()
    elif model_id == "azure-document-intelligence":
        return AzureOCR()
    else:
        return None


def model_id_to_asr(
    model_id: str
) -> ASRModel | None:
    if model_id.startswith("openai"):
        return OpenAIWhisperASR(whisper_model=model_id.split('-', 1)[-1])
    elif model_id.startswith("faster_whisper"):
        return remote_model("FasterWhisperASR", model_size=model_id.split('-', 1)[-1])
    else:
        return None


def model_id_to_classifier(
    model_id: str
) -> ZeroShotClassifier | None:
    return remote_model("TransformersClassifier", model=model_id)


def model_id_to_qa(
    model_id: str
) -> QuestionAnswering | None:
    if '/' in model_id:
        return remote_model("TransformersExtractiveQA", model=model_id)
    else:
        return None


def model_id_to_vqa(
    model_id: str
) -> QuestionAnswering | None:
    if model_id == "amazon-text-translate":
        return AmazonTextractDocVQA()
    elif model_id == "azure-text-translation":
        return AzureDocVQA()
    elif '/' in model_id:
        return remote_model("TransformersDocVQA", model=model_id)
    else:
        return None


def model_id_to_nmt(
    model_id: str
) -> NMTModel | None:
    if model_id.startswith('Helsinki-NLP/opus-mt'):
        return remote_model("EasyNMT")
    elif model_id == "amazon-text-translate":
        return AmazonTranslate()
    elif model_id == "azure-text-translation":
        return AzureTranslation()
    else:
        return None


def remote_model(name: str, *args, **kwargs) -> Any:
    inference_server_address = os.environ.get("INFERENCE_SERVER_ADDRESS", None)
    if not inference_server_address:
        raise Exception("INFERENCE_SERVER_ADDRESS env variable must be set if using local AI models.")
    host, port = inference_server_address.rsplit(":")
    return remote_object(name, host=host, port=int(port), *args, **kwargs)
