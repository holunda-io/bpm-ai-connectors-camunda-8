# Camunda 8 GPT AI Connectors 🤖

*Task specific connectors for Camunda 8 powered by large language models (LLMs) like OpenAI GPT-4.*

![Compatible with: Camunda Platform 8](https://img.shields.io/badge/Compatible%20with-Camunda%20Platform%208-26d07c)
[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-RED.svg)](https://holisticon.de/)


These connectors can automatically perform activities that previously required user tasks or specialized AI models, like:
* 🔍 **Information extraction** from unstructured data (emails, letters, documents, ...)
* ⚖  Informed **decision-making** before gateways
* ✍🏼 Creative **content generation** (emails, letters, ...)
* 🌍 **Translation**
* 📄 **Answering questions** over documents, wikis and other unstructured knowledge-bases
* 🗄 Querying **SQL Databases**
* 🌐 Interacting with **REST APIs**
* ...and more

Just provide input and output variable mappings and configure what you want to achieve - the connectors will do the heavy lifting:
1. Crafting tested, task- and model-specific prompts to get the most out of the LLM
2. Interfacing with the LLM provider (like OpenAI GPT-4 or 3.5)
3. Parsing the response into local process variables
4. Handling and automatically fixing common error cases

---

> :warning: **Experimental**: This project is not meant for production use as of today, but to evaluate and demonstrate LLMs in BPM use-cases.

## 🚀 How to Run Using Docker

Create a `connector-secrets.txt` file (use `connector-secrets.txt.sample` as a template) and fill in your OpenAI API key and Zeebe cluster information for either Cloud or a local cluster:

```bash
OPENAI_API_KEY=<put your key here>

ZEEBE_CLIENT_CLOUD_CLUSTER-ID=<cluster-id>
ZEEBE_CLIENT_CLOUD_CLIENT-ID=<client-id>
ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=<client-secret>
ZEEBE_CLIENT_CLOUD_REGION=<cluster-region>

# OR

ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=zeebe:26500
ZEEBE_CLIENT_SECURITY_PLAINTEXT=true
```

### (Optional): Run local zeebe cluster

If you are not using Camunda Cloud, start a local cluster:

```bash 
docker compose -f docker-compose.camunda-platform.yml up -d
```

### ▶️ Run connectors

Run the connector runtime using a pre-built image from DockerHub:

```bash 
docker run --env-file connector-secrets.txt holisticon/camunda-8-connector-gpt:develop
```

### Use Element Templates

1. Upload the element templates from [/element-templates](/element-templates) to your project in Camunda Cloud and publish them individually, or if you're working locally, place them besides your .bpmn file. 
2. Start modeling or try the example processes from [/example](/example).

## 📚 Connectors Documentation

* [Getting Started](docs/getting-started.md)
* [Foundational Connectors](docs/foundational-connectors.md)
* [Agentic Connectors](docs/agentic-connectors.md)
* [Custom LLMs](docs/custom-models.md)

## 🏗 Development & Project Setup

The connectors currently use the Java Connector API (implemented in Kotlin) for the connector workers (`core` module). 
All LLM specific code (LLM model interfaces, chains, agents, prompts, ...) are implemented in Python using the Langchain framework (`python` folder). 
The Python app serves a REST API for the core to use.

For convenience, both apps can be packaged into a single Docker image using the top-level Dockerfile or docker-compose.yml.

Alternatively, the Python app has its own Dockerfile (or the main.py can be run directly) and the `runtime` module can be dockerized using `spring-boot:build-image` (or run via the IDE, see below).

### Build
#### Connectors
You can package the Connectors by running the following command:

```bash
mvn clean package
```

This will create JAR-artifacts for the two modules:

- `camunda-8-connector-gpt-core-x.x.x-with-dependencies.jar`
  - The connector worker implementations
- `camunda-8-connector-gpt-runtime-x.x.x.jar`
  - A Spring Boot connector runtime using the core module

#### Python LLM Service

Python 3.10 is required. A virtual environment is advised.

Install the Python dependencies using the following command:

```bash
python -m pip install --upgrade -r python/requirements.txt
```

Install the Python app:
```bash
python -m pip install -e python/src
```

Start the Python service with:

```bash
python python/src/gpt/main.py
```

### Configuration

In order to run, the connectors will require an API key to OpenAI and connection details to connect to Camunda 8 platform.
All these settings should be performed using the file called `connector-secrets.txt` (check the sample file). 

If your connector runs locally from your host machine (command line or IDE) and connects to locally running Zeebe Cluster:
```
OPENAI_API_KEY=<put your key here>
CAMUNDA_OPERATE_CLIENT_URL=localhost:8080
ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=localhost:26500
ZEEBE_CLIENT_SECURITY_PLAINTEXT=true
```

If your connector runs using docker compose together with Zeebe Cluster:
```
OPENAI_API_KEY=<put your key here>
CAMUNDA_OPERATE_CLIENT_URL=operate:8080
ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=zeebe:26500
ZEEBE_CLIENT_SECURITY_PLAINTEXT=true
```

If you want to connect to Camunda 8 Cloud, please use the following configuration (independently of run mode); 
```
OPENAI_API_KEY=<put your key here>
ZEEBE_CLIENT_CLOUD_CLUSTER-ID=<cluster-id>
ZEEBE_CLIENT_CLOUD_CLIENT-ID=<client-id>
ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=<client-secret>
ZEEBE_CLIENT_CLOUD_REGION=bru-2
```

### Run from IDE

In your IDE you can also simply navigate to the `LocalContainerRuntime` class in the `runtime` module and run it via your IDE.
Please include the values from the configuration block as environment variables of your runtime either by copying the
values manually or using the [EnvFile Plugin for IntelliJ](https://plugins.jetbrains.com/plugin/7861-envfile).

## License

This library is developed under

[![Apache 2.0 License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](/LICENSE)

## Sponsors and Customers

[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-red.svg)](https://holisticon.de/)
