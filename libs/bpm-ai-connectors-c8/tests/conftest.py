import pytest
from xprocess import ProcessStarter

@pytest.fixture(autouse=True)
def connector_runtime(xprocess, zeebe_test_engine):
    class Starter(ProcessStarter):
        pattern = "Starting connector worker"
        popen_kwargs = {"cwd": "../bpm_ai_connectors_c8"}
        args = ['python', 'main.py', '--host', zeebe_test_engine.host, '--port', zeebe_test_engine.engine_port]

    xprocess.ensure("connector_runtime", Starter)
    yield
    xprocess.getinfo("connector_runtime").terminate()
