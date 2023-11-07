from __future__ import annotations

import contextvars
import inspect
import json
import logging
import os
import traceback
import uuid
from concurrent import futures
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
)

from langsmith import client, run_trees
from langsmith.run_helpers import _setup_run, LangSmithExtra, _collect_extra, _TraceableContainer, _PROJECT_NAME, \
    _PARENT_RUN_TREE, _TAGS, _METADATA

from bpm_ai_core.llm.common.function import Function
from bpm_ai_core.llm.common.message import ChatMessage, FunctionCallMessage
from bpm_ai_core.util.openai import messages_to_openai_dicts, json_schema_to_openai_function


class LangsmithTracer:

    def __init__(self):
        self.run_container = None
        self.context_run = None

    def start_llm_trace(
        self,
        llm: Any,
        messages: List[ChatMessage],
        current_try: int,
        functions: Optional[List[Function]] = None
    ):
        inputs = {
            "messages": messages_to_openai_dicts(messages),
            "model": llm.model,
            "temperature": llm.temperature,
            "current_try": current_try,
            "max_tries": llm.max_retries + 1,
            "functions": [json_schema_to_openai_function(f.name, f.description, f.args_schema) for f in functions]
        }
        self.start_trace(
            name=llm.__class__.__name__,
            run_type="llm",
            inputs=inputs
        )

    def end_llm_trace(self, completion: Optional[ChatMessage] = None, error_msg: Optional[str] = None):
        choices = {
            "choices": [{"message":
                             {"role": "assistant", "content": completion.content, **({"function_call": {"name": completion.name, "arguments": completion.payload_dict()}} if isinstance(completion, FunctionCallMessage) else {})}
                         }]
        } if completion else None
        self.end_trace(
            outputs=choices,
            error=error_msg
        )

    def start_function_trace(
        self,
        function: Function,
        inputs: dict,
    ):
        self.start_trace(
            name=function.name,
            run_type="tool",
            inputs=inputs,
            metadata={"description": function.description}
        )

    def end_function_trace(
        self,
        output: Optional[dict],
        error_msg: Optional[str] = None
    ):
        self.end_trace(
            outputs=output,
            error=error_msg
        )

    def start_trace(
        self,
        name: str,
        run_type: str,
        inputs: dict,
        executor: Optional[futures.ThreadPoolExecutor] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        tags: Optional[List[str]] = None,
        client: Optional[client.Client] = None,
        extra: Optional[Dict] = None
    ):
        self.context_run = _PARENT_RUN_TREE.get()
        self.run_container = self._setup_run(
            name=name,
            inputs=inputs,
            run_type=run_type,
            extra_outer=extra or {},
            executor=executor,
            metadata=metadata,
            tags=tags,
            langsmith_client=client
        )
        _PROJECT_NAME.set(self.run_container["project_name"])
        _PARENT_RUN_TREE.set(self.run_container["new_run"])

    def end_trace(self, outputs: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        if self.run_container is None:
            raise RuntimeError("Must call start_trace() before end_trace()")

        if error is not None:
            self.run_container["new_run"].end(error=error)
        elif outputs is not None:
            if isinstance(outputs, dict):
                self.run_container["new_run"].end(outputs=outputs)
            else:
                self.run_container["new_run"].end(outputs={"output": outputs})
        else:
            self.run_container["new_run"].end()

        self.run_container["new_run"].patch()
        _PARENT_RUN_TREE.set(self.context_run)
        _PROJECT_NAME.set(self.run_container["outer_project"])
        _TAGS.set(self.run_container["outer_tags"])
        _METADATA.set(self.run_container["outer_metadata"])

        self.run_container = None
        self.context_run = None

    @staticmethod
    def _setup_run(
        name: str,
        run_type: str,
        inputs: dict,
        extra_outer: dict,
        langsmith_extra: Optional[LangSmithExtra] = None,
        executor: Optional[futures.ThreadPoolExecutor] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        tags: Optional[List[str]] = None,
        langsmith_client: Optional[client.Client] = None,
    ) -> _TraceableContainer:
        outer_project = _PROJECT_NAME.get() or os.environ.get(
            "LANGCHAIN_PROJECT", os.environ.get("LANGCHAIN_PROJECT", "default")
        )
        langsmith_extra = langsmith_extra or LangSmithExtra()
        parent_run_ = langsmith_extra.get("run_tree") or _PARENT_RUN_TREE.get()
        project_name_ = langsmith_extra.get("project_name", outer_project)
        extra_inner = _collect_extra(extra_outer, langsmith_extra)
        outer_metadata = _METADATA.get()
        metadata_ = {
            **(langsmith_extra.get("metadata") or {}),
            **(outer_metadata or {}),
        }
        _METADATA.set(metadata_)
        metadata_.update(metadata or {})
        metadata_["ls_method"] = "traceable"
        extra_inner["metadata"] = metadata_
        outer_tags = _TAGS.get()
        tags_ = (langsmith_extra.get("tags") or []) + (outer_tags or [])
        _TAGS.set(tags_)
        tags_ += tags or []
        id_ = langsmith_extra.get("run_id", uuid.uuid4())
        client_ = langsmith_extra.get("client", langsmith_client)
        if parent_run_ is not None:
            new_run = parent_run_.create_child(
                name=name,
                run_type=run_type,
                serialized={"name": name},
                inputs=inputs,
                tags=tags_,
                extra=extra_inner,
                run_id=id_,
            )
        else:
            new_run = run_trees.RunTree(
                id=id_,
                name=name,
                serialized={"name": name},
                inputs=inputs,
                run_type=run_type,
                reference_example_id=langsmith_extra.get("reference_example_id"),
                project_name=project_name_,
                extra=extra_inner,
                tags=tags_,
                executor=executor,
                client=client_,
            )
        new_run.post()
        return _TraceableContainer(
            new_run=new_run,
            project_name=project_name_,
            outer_project=outer_project,
            outer_metadata=outer_metadata,
            outer_tags=outer_tags,
        )
