# BPM AI Connectors for Camunda 🤖

*Task specific connectors for Camunda 8 powered by large language models (LLMs) like OpenAI GPT-4.*

![Compatible with: Camunda Platform 8](https://img.shields.io/badge/Compatible%20with-Camunda%20Platform%208-26d07c)
[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-RED.svg)](https://holisticon.de/)


These connectors can automate activities that previously required user tasks or specialized AI models, like:
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

## 🚀 How to Run Using Docker

Create an `.env` file (use `env.sample` as a template) and fill in your Zeebe cluster information (for either cloud or a local cluster) and your OpenAI API key (if needed):

```bash
OPENAI_API_KEY=<put your key here>

ZEEBE_CLIENT_CLOUD_CLUSTER-ID=<cluster-id>
ZEEBE_CLIENT_CLOUD_CLIENT-ID=<client-id>
ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=<client-secret>
ZEEBE_CLIENT_CLOUD_REGION=<cluster-region>

# OR

ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=zeebe:26500
```

### (Optional): Run local zeebe cluster

If you are not using Camunda Cloud, start a local cluster:

```bash 
docker compose -f docker-compose.camunda-platform.yml up -d
```

### ▶️ Run connectors

Run the connector runtime using a pre-built image from DockerHub:

```bash 
docker run --env-file .env holisticon/bpm-ai-connectors-camunda-8:latest 
```

### Use Element Templates in your Processes

After starting the connector workers in their runtime, you also need to make the connectors known to the Modeler in order to actually model processes with them.

1. Upload the element templates from [/bpmn/.camunda/element-templates](/bpmn/.camunda/element-templates) to your project in Camunda Cloud Modeler and click `publish` on each one, or if you're working locally, place them besides your .bpmn file or add them to the `resources/element-templates`
   directory of your Modeler. 
2. Start modeling a new process or try the example processes from [/example](/example).

## 📚 Connectors Documentation

* [Getting Started](docs/getting-started.md)
* [Connectors](docs/foundational-connectors.md)

## 🏗 Development & Project Setup

...

For convenience, both apps can be packaged into a single Docker image using the top-level Dockerfile or docker-compose.yml.

Alternatively, the Python connector runtime can be run directly (see below) and the feel-engine-wrapper has multiple Dockerfiles (native or jvm) in [src/main/docker](feel-engine-wrapper/src/main/docker).



### Build
#### Connectors


```bash

```


#### Python 

Python 3.11+ is required.

Install the Python dependencies using the following command:

```bash

```

Install the Python app:
```bash

```

```bash
cd bpm-ai-connectors-c8
python -m bpm_ai_connectors_c8.main
```
### Configuration

In order to run, the connectors will require connection details to connect to Camunda 8 platform, and (if you want to use OpenAI models) an OpenAI API key.
These parameters must be available to the connector runtime as environment variables. Create an `.env` file (check the `env.sample` file) with the following variables:

If your connector runs locally from your host machine (command line or IDE) and connects to locally running Zeebe Cluster:
```
OPENAI_API_KEY=<put your key here>
ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=localhost:26500
```

If your connector runs using docker compose together with Zeebe Cluster:
```
OPENAI_API_KEY=<put your key here>
ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=zeebe:26500
```

If you want to connect to Camunda 8 Cloud, please use the following configuration (independently of run mode); 
```
OPENAI_API_KEY=<put your key here>
ZEEBE_CLIENT_CLOUD_CLUSTER-ID=<cluster-id>
ZEEBE_CLIENT_CLOUD_CLIENT-ID=<client-id>
ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=<client-secret>
ZEEBE_CLIENT_CLOUD_REGION=bru-2
```

## License

This library is developed under

[![Apache 2.0 License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](/LICENSE)

## Sponsors and Customers

[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-red.svg)](https://holisticon.de/)
