from pyzeebe import Job

from bpm_ai_connectors_c8.models import model_id_to_llm
from bpm_ai_connectors_c8.runtime import create_output_variables, examine_error_expression
from bpm_ai_connectors_c8.secrets import replace_secrets_in_dict


async def job_activate(job: Job) -> Job:
    print(f"Running task '{job.type}' with variables {job.variables} and headers {job.custom_headers}")
    job.custom_headers["connector_vars"] = set(job.variables.keys())
    job.variables = replace_secrets_in_dict(job.variables)
    return job


async def job_complete(job: Job) -> Job:
    connector_vars = job.custom_headers["connector_vars"]
    result_variables = {k: v for k, v in job.variables.items() if k not in connector_vars}

    output_variables = create_output_variables(
        {"result": result_variables},
        job.custom_headers.get("resultExpression", "")
    )
    error = examine_error_expression(
        {**result_variables, **output_variables},
        job.custom_headers.get("errorExpression", "")
    )
    if error:
        print(f"Aborting task '{job.type}' because error expression returned bpmnError: {error}")
        await job.set_error_status(error["message"], error["code"])
    else:
        print(f"Completing task '{job.type}' with variables {output_variables}")
        job.variables = output_variables
    return job


def resolve_model(job: Job) -> Job:
    if "model" in job.variables.keys():
        job.variables["model"] = model_id_to_llm(job.variables["model"])
    return job
