# 🛠️ Development & Project Setup

The connector workers are written in Python based on [pyzeebe](https://github.com/camunda-community-hub/pyzeebe).
They are a thin wrapper around the core logic and AI abstractions, 
which are independent of the specific workflow engine (or can even be integrated in a plain Python project directly) and placed 
in a separate repository: [bpm-ai](https://github.com/holunda-io/bpm-ai)

To be able to use inference code for local AI models that is published under GPL-3+ licenses, and to be able to potentially distribute inference to a different (GPU) machine,
there is a separate [bpm-ai-inference](https://github.com/holunda-io/bpm-ai-inference) project with accompanying docker image that can optionally be run to extend the main connector container by local AI inference capabilities.

All connectors make use of feel expressions to flexibly map the task result into one or multiple result variables and/or define error expressions. 
Therefore, a feel engine is required - which is only available as a Scala implementation. 
To keep the runtime and Docker image overhead of needing an accompanying JVM app as low as possible,
[feel-engine-wrapper](/feel-engine-wrapper) is a small, native-compiled Quarkus server wrapping the [connector-sdk/feel-wrapper](https://github.com/camunda/connectors/tree/main/connector-sdk/feel-wrapper), which itself wraps the feel engine for use in connectors.

For convenience, both apps can be packaged into a single Docker image using the top-level Dockerfile or docker-compose.yml.

Alternatively, the Python connector runtime can be started directly (see below) and the feel-engine-wrapper has multiple Dockerfiles (native or JVM) in [src/main/docker](feel-engine-wrapper/src/main/docker).

### Build

#### Connectors 
```bash
cd bpm-ai-connectors-c8
```
Python 3.11 and Poetry 1.6.1 is required. 

The project itself also works with Python 3.12, but some dependencies of the bpm-ai[inference] extra don't compile in the python:3.12 docker image as of yet.

Install the dependencies:
```bash
poetry install
```
Run the connectors:
```bash
python -m bpm_ai_connectors_c8.main
```

Note that some dependencies are listed as dev dependencies which will be installed by `poetry install` as well. 
These are the full dependencies required to also run the parts of the application (and tests) referred to by _inference_.
Meaning, all heavy-weight dependencies for local model inference (torch, transformers, etc.) are included. 
Since poetry does not allow selectively installing extras of dependencies (only with environment markers), the Dockerfile 
only installs the main dependency block from the pyproject.toml and then manually installs the dependencies from 
[requirements.default.txt](bpm-ai-connectors-c8/requirements.default.txt) or [requirements.inference.txt](bpm-ai-connectors-c8/requirements.inference.txt),
depending on the image to build.

#### Feel Engine Wrapper
```bash
cd feel-engine-wrapper
```
Build native executable:
```bash
./mvnw package -Dnative
```
Run it:
```bash
./target/feel-engine-wrapper-runner
```

### Tests

Run integration test:

```bash
export ZEEBE_TEST_IMAGE_TAG=8.4.0 
export OPENAI_API_KEY=<put your key here> 
poetry run pytest
```

The tests will:
* spin up a Zeebe test engine using [pytest-zeebe](https://github.com/holunda-io/pytest-zeebe)
* start a mocked feel engine wrapper server
* deploy and run a small test process for each connector, using the actual OpenAI API

The CI/CD pipeline additionally runs these tests against the actual built Docker image before pushing the `latest` tag to Docker Hub.

### Docker Image
Build image:

```bash
docker build -t bpm-ai-connectors-camunda-8:latest .
```