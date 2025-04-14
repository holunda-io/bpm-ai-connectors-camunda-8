import argparse
import asyncio
import logging
import os
import time

from pyzeebe import ZeebeWorker, create_insecure_channel
from pyzeebe.channel.camunda_cloud_channel import create_camunda_cloud_channel
from pyzeebe.errors import UnkownGrpcStatusCodeError, ZeebeInternalError, ZeebeGatewayUnavailableError, \
    ZeebeBackPressureError

from bpm_ai_connectors_c8.decorators import job_activate, job_complete
from bpm_ai_connectors_c8.tasks.compose.compose_task import compose_router
from bpm_ai_connectors_c8.tasks.decide.decide_task import decide_router
from bpm_ai_connectors_c8.tasks.extract.extract_task import extract_router
from bpm_ai_connectors_c8.tasks.generic.generic_task import generic_router
from bpm_ai_connectors_c8.tasks.retrieval.retrieval_task import retrieval_router
from bpm_ai_connectors_c8.tasks.translate.translate_task import translate_router

logger = logging.getLogger(__name__)


async def create_channel(host=None, port=None):
    cluster_id = os.environ.get("ZEEBE_CLIENT_CLOUD_CLUSTER_ID") or os.environ.get("ZEEBE_CLIENT_CLOUD_CLUSTER-ID")
    if cluster_id:
        channel = create_camunda_cloud_channel(
           os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT_ID") or os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-ID"),
           os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT_SECRET") or os.environ.get("ZEEBE_CLIENT_CLOUD_CLIENT-SECRET"),
           cluster_id,
           os.environ.get("ZEEBE_CLIENT_CLOUD_REGION", "bru-2")
        )
        logger.info(f"Created channel to cloud cluster {cluster_id}")
    else:
        broker_gateway = os.environ.get("ZEEBE_CLIENT_BROKER_GATEWAY_ADDRESS") or os.environ.get("ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS")
        if broker_gateway:
            host, port = broker_gateway.split(":")
        channel = create_insecure_channel(
            hostname=host,
            port=port
        )
        logger.info(f"Created channel to local broker {host}:{port}")
    return channel


def include_connectors(worker: ZeebeWorker):
    worker.include_router(extract_router)
    worker.include_router(decide_router)
    worker.include_router(compose_router)
    worker.include_router(translate_router)
    worker.include_router(generic_router)
    worker.include_router(retrieval_router)


async def main(host=None, port=None):
    channel = await create_channel(host, port)

    worker = ZeebeWorker(channel)
    worker.before(job_activate)
    worker.after(job_complete)

    include_connectors(worker)

    logger.info("Starting connector worker.")
    try:
        await worker.work()
    except (UnkownGrpcStatusCodeError, ZeebeInternalError, ZeebeGatewayUnavailableError) as e:
        logger.error("Worker exited with exception, retrying: %s", e)
        await main(host=host, port=port)
    except ZeebeBackPressureError as e:
        logger.error("Zeebe engine under high load, retrying in 60s: %s", e)
        time.sleep(60)
        await main(host=host, port=port)
    else:
        logger.info("Exited connector worker.")


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='Zeebe engine host', default=None)
    parser.add_argument('--port', type=int, help='Zeebe engine port number', default=None)
    args = parser.parse_args()

    asyncio.run(main(args.host, args.port))
