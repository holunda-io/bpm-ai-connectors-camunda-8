ARG PYTHON_VERSION="3.11"

###############################################################################
# 1. Build feel-engine-wrapper native executable using quarkus mandrel
###############################################################################
FROM quay.io/quarkus/ubi-quarkus-mandrel-builder-image:jdk-21 AS build-jvm

COPY --chown=quarkus:quarkus feel-engine-wrapper/mvnw /app/mvnw
COPY --chown=quarkus:quarkus feel-engine-wrapper/.mvn /app/.mvn
COPY --chown=quarkus:quarkus feel-engine-wrapper/pom.xml /app/

USER quarkus
WORKDIR /app
RUN ./mvnw -B org.apache.maven.plugins:maven-dependency-plugin:3.1.2:go-offline
COPY feel-engine-wrapper/src /app/src
RUN ./mvnw package -Dnative

###############################################################################
# 2. Install python connector dependencies
###############################################################################
# poetry setup code based on https://github.com/thehale/docker-python-poetry (does not provide multiarch images)
FROM python:${PYTHON_VERSION} AS build-python
ARG POETRY_VERSION="1.6.1"

ENV POETRY_VERSION=${POETRY_VERSION}
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends curl
# Install Poetry via the official installer: https://python-poetry.org/docs/master/#installing-with-the-official-installer
# This script respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
# only install dependencies into project virtualenv
WORKDIR /app
COPY bpm-ai-connectors-c8/pyproject.toml \
     bpm-ai-connectors-c8/poetry.lock ./
RUN poetry install --only main --no-root --no-cache

###############################################################################
# 3. Final, minimal image that starts the connectors and feel engine process
###############################################################################
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=build-jvm /app/target/feel-engine-wrapper-runner feel-wrapper
COPY ./bpm-ai-connectors-c8/bpm_ai_connectors_c8/ ./bpm_ai_connectors_c8/
COPY --from=build-python /app/.venv/lib/python${PYTHON_VERSION}/site-packages /home/nonroot/.local/lib/python${PYTHON_VERSION}/site-packages

# Run two processes: connector runtime + feel engine wrapper
COPY init.py .
CMD ["init.py", "./feel-wrapper", "python -m bpm_ai_connectors_c8.main"]