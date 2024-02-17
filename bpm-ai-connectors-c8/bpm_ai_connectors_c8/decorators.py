import logging
from typing import Callable

from pyzeebe import Job, ZeebeTaskRouter, default_exception_handler, TaskConfig
from pyzeebe.errors import BusinessError
from pyzeebe.function_tools import parameter_tools
from pyzeebe.task import task_builder

from bpm_ai_connectors_c8.connector_secrets import replace_secrets_in_dict
from bpm_ai_connectors_c8.feel import create_output_variables, examine_error_expression
from bpm_ai_connectors_c8.models import model_ids_to_models, CUSTOM_MODEL_VARS

logger = logging.getLogger(__name__)

DEFAULT_TASK_TIMEOUT = (5*60*1000)


def _task_type(task_name: str, task_version: int):
    return f"io.holunda:connector-{task_name}:{task_version}"


def ai_task(
    router: ZeebeTaskRouter,
    name: str,
    version: int,
    timeout_ms: int = DEFAULT_TASK_TIMEOUT,
    max_jobs_to_activate: int = 32,
    max_running_jobs: int = 32
):
    def task_wrapper(task_function: Callable):
        config = TaskConfig(
            _task_type(name, version),
            default_exception_handler,
            timeout_ms,
            max_jobs_to_activate,
            max_running_jobs,
            # fetch variables defined by the task function + any possible custom model definitions, as we don't want
            # those as task function parameters. Instead, only the final model object (custom or not) is injected
            parameter_tools.get_parameters_from_function(task_function) + CUSTOM_MODEL_VARS,
            False,
            "",
            [],
            [],
        )
        task = task_builder.build_task(wrap(task_function), config)
        router._add_task(task)
        return task_function

    return task_wrapper


async def job_activate(job: Job) -> Job:
    vars_to_log = {k: v for k, v in job.variables.items() if k != 'job'}
    logger.info(f"Running task '{job.type}' with variables {vars_to_log} and headers {job.custom_headers}")
    job.custom_headers["connector_vars"] = set(job.variables.keys())
    return job


def wrap(task_function: Callable):
    async def handle_job(job: Job, **kwargs):
        kwargs = model_ids_to_models(kwargs)
        kwargs = filter_vars_to_fetch(kwargs)
        kwargs = replace_secrets_in_dict(kwargs)
        result = await task_function(**kwargs)
        output_variables = await prepare_output_variables(job, result)
        return output_variables

    def filter_vars_to_fetch(kwargs):
        vars_to_fetch = parameter_tools.get_parameters_from_function(task_function)
        kwargs = {k: v for k, v in kwargs.items() if k in vars_to_fetch}
        return kwargs

    return handle_job


async def prepare_output_variables(job: Job, task_result: dict | list) -> dict:
    output_variables = create_output_variables(
        {"result": task_result},
        job.custom_headers.get("result_expression", "")
    )
    error = examine_error_expression(
        output_variables,
        job.custom_headers.get("error_expression", "")
    )
    if error:
        logger.info(f"Aborting task '{job.type}' because error expression returned bpmnError: {error}")
        raise BusinessError(error["code"], error["message"])
    else:
        logger.info(f"Completing task '{job.type}' with variables {output_variables}")
        return output_variables


async def job_complete(job: Job) -> Job:
    connector_vars = job.custom_headers["connector_vars"]
    job.variables = {k: v for k, v in job.variables.items() if k not in connector_vars}
    return job
