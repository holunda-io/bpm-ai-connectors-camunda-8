import asyncio
import logging
import os

import grpc
import requests
from dotenv import load_dotenv
from pyzeebe import ZeebeWorker, create_insecure_channel
from pyzeebe.channel.camunda_cloud_channel import _create_oauth_credentials

from bpm_ai_connectors_c8.decorators import job_activate, resolve_model, job_complete
from bpm_ai_connectors_c8.tasks.experimental.rpa.rpa_task import rpa_router
from bpm_ai_connectors_c8.tasks.foundational.compose.compose_task import compose_router
from bpm_ai_connectors_c8.tasks.foundational.decide.decide_task import decide_router
from bpm_ai_connectors_c8.tasks.foundational.extract.extract_task import extract_router
from bpm_ai_connectors_c8.tasks.foundational.generic.generic_task import generic_router
from bpm_ai_connectors_c8.tasks.foundational.translate.translate_task import translate_router

load_dotenv(dotenv_path='../../../connector-secrets.txt')

logger = logging.getLogger(__name__)


async def _create_saas_channel():
    cluster_id = os.environ.get("ZEEBE_CLIENT_CLOUD_CLUSTER-ID")
    region = os.environ.get("ZEEBE_CLIENT_CLOUD_REGION")
    url = 'https://login.cloud.camunda.io/oauth/token'
    headers = {'Content-Type': 'application/json'}
    data = {
        'audience': f'{cluster_id}.{region}.zeebe.camunda.io',
        'client_id': os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-ID"),
        'client_secret': os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-SECRET")
    }
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    response = requests.post(url, json=data, headers=headers)
    channel_credentials = _create_oauth_credentials(response.json()["access_token"])
    channel = grpc.aio.secure_channel(f"{cluster_id}.{region}.zeebe.camunda.io:443", channel_credentials)
    return channel


async def create_channel():
    if os.environ.get("ZEEBE_CLIENT_CLOUD_REGION"):
        # channel = create_camunda_cloud_channel(
        #    os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-ID"),
        #    os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-SECRET"),
        #    os.environ.get("ZEEBE_CLIENT_CLOUD_CLUSTER-ID"),
        #    os.environ.get("ZEEBE_CLIENT_CLOUD_REGION")
        # )
        # todo temporary hack because ipv6 address of login.cloud.camunda.io seems to be broken
        channel = await _create_saas_channel()

    else:
        if os.environ.get("ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS"):
            host, port = os.environ.get("ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS").split(":")
        else:
            host, port = (None, None)
        channel = create_insecure_channel(
            hostname=host,
            port=port
        )
    return channel


def include_foundational_connectors(worker: ZeebeWorker):
    worker.include_router(extract_router)
    worker.include_router(decide_router)
    worker.include_router(compose_router)
    worker.include_router(translate_router)
    worker.include_router(generic_router)


def include_experimental_connectors(worker: ZeebeWorker):
    worker.include_router(rpa_router)


async def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    channel = await create_channel()

    worker = ZeebeWorker(channel)
    worker.before(job_activate, resolve_model)
    worker.after(job_complete)

    include_foundational_connectors(worker)

    if os.environ.get("BPM_AI_ENABLE_EXPERIMENTAL_TASKS", False):
        include_experimental_connectors(worker)

    logger.debug(worker.tasks)

    logger.info("[worker] starting...")
    await worker.work()
    logger.info("[worker] exited.")


if __name__ == "__main__":
    asyncio.run(main())
