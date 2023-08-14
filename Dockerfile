# ---- Build Maven Java Spring Boot App ----
FROM maven:3.9.3-eclipse-temurin-17 AS build-java
WORKDIR /workspace

COPY . .
RUN mvn clean package -DskipTests

# ---- Final Image with Python as base ----
FROM python:3.10

# Copy the Java app from the Maven build stage
COPY --from=build-java /workspace/runtime/target/camunda-8-connector-gpt-runtime-0.1.2-SNAPSHOT.jar /connector-runtime/connector-runtime.jar

RUN apt-get update  \
    && apt-get install -y openjdk-17-jre  \
    && apt-get install -y python3-dev build-essential libpq-dev default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY python/requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

COPY python/src/ /python-src/
RUN pip install -e /python-src

WORKDIR /python-src
CMD ["sh", "-c", "java -jar /connector-runtime/connector-runtime.jar & python gpt/main.py"]
