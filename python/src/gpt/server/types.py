from typing import Optional, Dict, Any, List

from langchain.pydantic_v1 import BaseModel


class ExtractTask(BaseModel):
    model: str
    extraction_schema: dict
    context: dict
    repeated: bool
    repeated_description: Optional[str]


class DecideTask(BaseModel):
    model: str
    context: dict
    instructions: str
    output_type: str
    possible_values: Optional[List[Any]] = None


class TranslateTask(BaseModel):
    model: str
    input: dict
    target_language: str


class ComposeTask(BaseModel):
    model: str
    context: dict
    instructions: str
    type: str
    style: str
    tone: str
    length: str
    language: str
    temperature: float = 0.0
    sender: Optional[str] = None
    constitutional_principle: Optional[str] = None


class GenericTask(BaseModel):
    model: str
    context: dict
    instructions: str
    output_schema: dict


class OpenApiTask(BaseModel):
    model: str
    task: str
    context: dict
    output_schema: Optional[dict] = None
    spec_url: str
    skill_mode: Optional[str] = None
    skill_store: Optional[str] = None
    skill_store_url: Optional[str] = None
    skill_store_password: Optional[str] = None


class DatabaseTask(BaseModel):
    model: str
    task: str
    context: dict
    output_schema: Optional[dict] = None
    database_url: str
    skill_mode: Optional[str] = None
    skill_store: Optional[str] = None
    skill_store_url: Optional[str] = None
    skill_store_password: Optional[str] = None


class RetrievalTask(BaseModel):
    model: str
    database: str
    database_url: str
    password: Optional[str] = None
    embedding_provider: str
    embedding_model: str
    mode: str
    query: str
    document_content_description: Optional[str] = None
    metadata_field_info: Optional[List[dict]] = None
    output_schema: Optional[dict] = None
    parent_document_store: Optional[str] = None
    parent_document_store_url: Optional[str] = None
    parent_document_store_password: Optional[str] = None
    parent_document_store_namespace: Optional[str] = None
    parent_document_id_key: Optional[str] = None


class ProcessTask(BaseModel):
    model: str
    task: str
    activities: Dict[str, str]
    context: dict


class PlannerTask(BaseModel):
    model: str
    task: str
    tools: Dict[str, str]
    context: dict


class ExecutorTask(BaseModel):
    model: str
    task: str
    tools: Dict[str, str]
    context: dict
    previous_steps: Any
    current_step: str
