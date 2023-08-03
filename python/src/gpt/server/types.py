from typing import Optional, Dict, Any, List

from pydantic import BaseModel


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
    output_schema: dict
    spec_url: str
    skill_store_url: Optional[str] = None


class DatabaseTask(BaseModel):
    model: str
    task: str
    context: dict
    output_schema: dict
    database_url: str
    skill_store_url: Optional[str] = None


class RetrievalTask(BaseModel):
    model: str
    database_url: str
    embedding_provider: str
    embedding_model: str
    mode: str
    query: str


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
