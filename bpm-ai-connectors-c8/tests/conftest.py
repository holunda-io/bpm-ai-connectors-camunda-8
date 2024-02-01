import os

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from xprocess import ProcessStarter

# specifically use the amd64 tag as the docker image test runs after the platform images are pushed,
# but before the merged multiarch manifest (latest tag) is pushed.
# ideally both platform images should be tested (and even better before anything is pushed at all...)
DOCKER_IMAGE = "holisticon/bpm-ai-connectors-camunda-8:latest-amd64"


@pytest.fixture
def feel_mock_server(xprocess):
    class Starter(ProcessStarter):
        pattern = "Running on"
        popen_kwargs = {"cwd": "."}
        args = ['python', 'feel_mockserver.py']

    xprocess.ensure("feel_mock_server", Starter)
    yield
    xprocess.getinfo("feel_mock_server").terminate()


@pytest.fixture
def connector_runtime(xprocess, zeebe_test_engine):
    class Starter(ProcessStarter):
        pattern = "Starting connector worker"
        popen_kwargs = {"cwd": ".."}
        args = ['python', '-m' 'bpm_ai_connectors_c8.main', '--host', zeebe_test_engine.host, '--port', zeebe_test_engine.engine_port]

    xprocess.ensure("connector_runtime", Starter)
    yield
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
def docker_runtime(zeebe_test_engine):
    """
    Runtime based on actual docker image with connectors and real feel engine wrapper.
    """
    container = DockerContainer(DOCKER_IMAGE)
    container.with_env("ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS", f"host.docker.internal:{zeebe_test_engine.engine_port}")
    container.with_env("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
    container.start()
    wait_for_logs(container, "Starting connector worker.")
    yield container
    container.stop()


@pytest.fixture
def runtime_selector(request):
    runtime = os.environ.get('TEST_RUNTIME', 'python')
    if runtime == 'docker':
        return request.getfixturevalue('docker_runtime')
    else:
        return request.getfixturevalue('python_runtime')
