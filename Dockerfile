ARG TARGETARCH="arm64"
ARG PYTHON_VERSION="3.12"
###############################################################################
# 1. build feel-engine-wrapper native executable using quarkus mandrel
###############################################################################
FROM quay.io/quarkus/ubi-quarkus-mandrel-builder-image:jdk-21 AS build-java
ARG TARGETARCH

COPY --chown=quarkus:quarkus feel-engine-wrapper/mvnw /app/mvnw
COPY --chown=quarkus:quarkus feel-engine-wrapper/.mvn /app/.mvn
COPY --chown=quarkus:quarkus feel-engine-wrapper/pom.xml /app/
COPY --chown=quarkus:quarkus docker/upx_${TARGETARCH} /usr/bin/upx

USER quarkus
WORKDIR /app
RUN ./mvnw -B org.apache.maven.plugins:maven-dependency-plugin:3.1.2:go-offline
COPY feel-engine-wrapper/src /app/src
RUN ./mvnw package -Dnative-compress

###############################################################################
# 2. install python connector dependencies
###############################################################################
# poetry setup code copied from https://github.com/thehale/docker-python-poetry, due to missing multiarch images
# POETRY BASE IMAGE - Provides environment variables for poetry
FROM python:${PYTHON_VERSION}-slim AS python-poetry-base
ARG POETRY_VERSION="1.6.1"
ENV POETRY_VERSION=${POETRY_VERSION}
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"
# POETRY BUILDER IMAGE - Installs Poetry and dependencies
FROM python-poetry-base AS python-poetry-builder
RUN apt-get update && apt-get install -y --no-install-recommends curl
# Install Poetry via the official installer: https://python-poetry.org/docs/master/#installing-with-the-official-installer
# This script respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
# POETRY RUNTIME IMAGE - Copies the poetry installation into a smaller image and builds target app
FROM python-poetry-base AS build-python
COPY --from=python-poetry-builder $POETRY_HOME $POETRY_HOME
# only install dependencies into project virtualenv
COPY bpm-ai-connectors-c8/pyproject.toml bpm-ai-connectors-c8/poetry.lock ./app/
WORKDIR /app
RUN poetry install --without dev,test --no-root --no-cache

###############################################################################
# 3. Final, minimal image
###############################################################################
FROM cgr.dev/chainguard/python:latest

ARG PYTHON_VERSION
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=build-java /app/target/feel-engine-wrapper-runner feel-wrapper
COPY ./bpm-ai-connectors-c8/bpm_ai_connectors_c8/ ./bpm_ai_connectors_c8/
COPY --from=build-python /app/.venv/lib/python${PYTHON_VERSION}/site-packages /home/nonroot/.local/lib/python${PYTHON_VERSION}/site-packages

# Run two processes: connector runtime + feel engine wrapper
COPY docker/init.py .
CMD ["init.py", "./feel-wrapper", "python -m bpm_ai_connectors_c8.main"]
