import asyncio

from dotenv import load_dotenv
from pyzeebe import create_camunda_cloud_channel, ZeebeWorker, ZeebeTaskRouter, create_insecure_channel, Job
import os

from bpm_ai_connectors_c8.models import model_id_to_llm
from bpm_ai_connectors_c8.secrets import replace_secrets_in_dict
from bpm_ai_connectors_c8.tasks.routers import task_router, experimental_task_router
from bpm_ai_connectors_c8.tasks.rpa.rpa_task import rpa_router

load_dotenv(dotenv_path='../../../connector-secrets.txt')


def job_activate(job: Job) -> Job:
    print(f"Running task '{job.type}' with variables {job.variables} and headers {job.custom_headers}")
    return None
    job.custom_headers["connector_vars"] = set(job.variables.keys())
    job.variables = replace_secrets_in_dict(job.variables)
    return job


def job_complete(job: Job) -> Job:
    connector_vars = job.custom_headers["connector_vars"]
    job.variables = {k: v for k, v in job.variables.items() if k not in connector_vars}
    print(f"Completing task '{job.type}' with variables {job.variables}")
    return job


def resolve_model(job: Job) -> Job:
    if "model" in job.variables.keys():
        job.variables["model"] = model_id_to_llm(job.variables["model"])
    return job


async def main():
    if os.environ.get("ZEEBE_CLIENT_CLOUD_REGION"):
        channel = create_camunda_cloud_channel(
            os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-ID"),
            os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-SECRET"),
            os.environ.get("ZEEBE_CLIENT_CLOUD_CLUSTER-ID"),
            os.environ.get("ZEEBE_CLIENT_CLOUD_REGION")
        )
    else:
        if os.environ.get("ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS"):
            host, port = os.environ.get("ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS").split(":")
        else:
            host, port = (None, None)
        channel = create_insecure_channel(
            hostname=host,
            port=port
        )

    worker = ZeebeWorker(channel)
    worker.before(job_activate, resolve_model)
    worker.after(job_complete)

    worker.include_router(task_router)
    if os.environ.get("BPM_AI_ENABLE_EXPERIMENTAL_TASKS", False):
        worker.include_router(rpa_router)

    print(worker.tasks)

    print("Starting worker...")
    await worker.work()
    print("Worker exited.")


if __name__ == "__main__":
    asyncio.run(main())
