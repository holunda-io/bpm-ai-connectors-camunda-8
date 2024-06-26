import logging
import os
import sys
from pathlib import Path

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from xprocess import ProcessStarter

logger = logging.getLogger("test")


def _docker_host() -> str:
    return "172.17.0.1" if sys.platform == "linux" else "host.docker.internal"


@pytest.fixture
def feel_mock_server(xprocess):
    class Starter(ProcessStarter):
        pattern = "Running on"
        popen_kwargs = {"cwd": "."}
        args = ['python', 'feel_mockserver.py']

    xprocess.ensure("feel_mock_server", Starter)
    yield
    xprocess.getinfo("feel_mock_server").terminate()


def ensure_openai_key() -> str:
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise Exception("OPENAI_API_KEY env variable not set!")
    return openai_key


@pytest.fixture
def connector_runtime(xprocess, zeebe_test_engine, request):
    ensure_openai_key()

    if os.environ.get('INFERENCE_IMAGE', None):
        inference_container = request.getfixturevalue('docker_inference_runtime')
        os.environ['INFERENCE_SERVER_ADDRESS'] = f"localhost:{inference_container.get_exposed_port(6666)}"

    class Starter(ProcessStarter):
        pattern = "Starting connector worker"
        popen_kwargs = {"cwd": ".."}
        args = ['python', '-m' 'bpm_ai_connectors_c8.main',
                '--host', zeebe_test_engine.host,
                '--port', zeebe_test_engine.engine_port]

    _, log_path = xprocess.ensure("connector_runtime", Starter)
    yield
    full_logs = Path(log_path).read_text().split("@@__xproc_block_delimiter__@@")
    latest_logs = full_logs[-1] if full_logs else ""
    logger.info(latest_logs)
    xprocess.getinfo("connector_runtime").terminate()


@pytest.fixture
def python_runtime(connector_runtime, feel_mock_server):
    """
    Python based runtime.
    :param connector_runtime: connectors started as standard python process
    :param feel_mock_server: mocked feel engine server using python flask
    """
    pass


@pytest.fixture
def docker_runtime(zeebe_test_engine, request):
    """
    Runtime based on actual docker image with connectors and real feel engine wrapper.
    """
    container = DockerContainer(os.environ.get('CONNECTOR_IMAGE'))
    container.with_env("ZEEBE_CLIENT_BROKER_GATEWAY_ADDRESS", f"{_docker_host()}:{zeebe_test_engine.engine_port}")
    container.with_env("OPENAI_API_KEY", ensure_openai_key())

    if os.environ.get('INFERENCE_IMAGE', None):
        inference_container = request.getfixturevalue('docker_inference_runtime')
        container.with_env("INFERENCE_SERVER_ADDRESS", f"{_docker_host()}:{inference_container.get_exposed_port(6666)}")

    container.start()
    wait_for_logs(container, "Starting connector worker.")
    yield container
    stdout, stderr = container.get_logs()
    logger.info(stdout)
    logger.error(stderr)
    container.stop()


@pytest.fixture
def docker_inference_runtime():
    """
    Local inference extension container.
    """
    container = DockerContainer(os.environ.get('INFERENCE_IMAGE'))
    container.with_exposed_ports(6666)
    container.start()
    wait_for_logs(container, "======== Running on http://0.0.0.0:6666 ========")
    yield container
    stdout, stderr = container.get_logs()
    logger.info(stdout)
    logger.error(stderr)
    container.stop()


@pytest.fixture
def runtime_selector(request):
    if os.environ.get('CONNECTOR_IMAGE', None):
        return request.getfixturevalue('docker_runtime')
    else:
        return request.getfixturevalue('python_runtime')


def local_inference():
    image = os.environ.get('INFERENCE_IMAGE', None)
    return pytest.mark.skipif(
        not image,
        reason=f"Skipping test requiring inference container as INFERENCE_IMAGE env var not provided."
    )
