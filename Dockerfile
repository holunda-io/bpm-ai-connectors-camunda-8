# ---- Build Maven Java Spring Boot App ----
FROM maven:3.9.3-eclipse-temurin-20 AS build-java
WORKDIR /build-java

# Copy only the POM file to leverage Docker cache for dependencies
COPY pom.xml .
COPY core/pom.xml core/
COPY runtime/pom.xml runtime/
RUN mvn dependency:go-offline

# Now, copy the source code and build the project
COPY core/src/ core/src/
COPY runtime/src/ runtime/src/
RUN mvn clean package -DskipTests

# ---- Final Image with Python as Base ----
FROM python:3.10

# Install Java JRE and Python build dependencies in a single layer
RUN apt-get update  \
    && apt-get install -y openjdk-17-jre python3-dev build-essential libpq-dev default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

# Copy the Java app from the Maven build stage
COPY --from=build-java /build-java/runtime/target/camunda-8-connector-gpt-runtime-0.1.2-SNAPSHOT.jar /java/connector-runtime.jar

# Install Python dependencies
COPY python/requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

# Copy Python source and install it
COPY python/src/ /python/src/
RUN pip install -e /python/src

# Install supervisord and copy config
RUN pip3 install supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisord with Java and Python apps
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
