# Camunda 8 GPT AI Connectors 

*Task specific connectors for Camunda 8 powered by large language models (LLMs) like OpenAI GPT-4.*

![Compatible with: Camunda Platform 8](https://img.shields.io/badge/Compatible%20with-Camunda%20Platform%208-26d07c)
[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-RED.svg)](https://holisticon.de/)


These connectors can automatically perform activities that previously required user tasks or specialized AI models, like:
* 🔍 **Information extraction** from unstructured data (E-Mails, letters, documents, ...)
* ⚖  Informed **decision-making** before gateways
* ✍🏼 Creative **content generation** (e-mails, letters, ...)
* 🌍 **Translation**

Just provide input and output variable mappings and configure what you want to achieve - the connectors will do the heavy lifting:
1. Crafting tested, task- and model-specific prompts to get the most out of the LLM
2. Interfacing with the LLM provider (like OpenAI GPT-4 or 3.5)
3. Parsing the response into local process variables
4. Handling and automatically fixing common error cases 
5. Mapping remaining exceptions to BPMN errors so that you can react to them with boundary events 

## Connectors

### General Configuration

#### Input Variables

All connectors base their work on a map of input variables given as a FEEL map, e.g.:
```
{ "myVariable": myVariable }
```
The keys of the map should be the name of the variable or another fitting label for the variable content, as this will give the model context. 
For example, if you input a variable containing the subject of an e-mail, the label should make that clear: `"emailSubject":`. Otherwise, (if you name it `"var3"` for example) it might be hard to interpret the data.

#### Model

By default, all connectors will use the `Standard precision, fast, cheap` model, which translates to GPT-3.5-turbo. This model is fine for most tasks and pretty cost-effective. 
If you see undesired behavior for a complex task you can try `Highest precision, slow, expensive`, which translates to GPT-4 (if you have access to it). 

For using custom or open-source models, see [here](docs/custom-models.md).

---

### 🔍 Extract Connector
 
Can extract or deduce information from multiple input variables, potentially do simple conversions along the way, and store the result in one or more output variables.

#### Configuration

Provide a map of new variables to extract from the input, with descriptions of what they should contain:
```
{
  firstname: "first name",
  lastname: "last name",
  language: "the language that the email body is written in, as ISO code"
}
```

#### Result
A temporary variable `result` that contains a result JSON object of the same form as configured above. Can be mapped to one or more process variables using the result expression.

---

### ⚖ Decide Connector

Can make decisions based on multiple input variables and store the result decision and the reasoning behind it in output variables.

#### Configuration

Provide a natural language description of what the connector should decide, e.g.:
```
Decide what the intention of the customer's mail is.
```
Next, determine an output type (`Boolean`, `Integer` or `String`).
If not `Boolean`, you may restrict the connector to a classification on a finite set of options, instead of letting it freely choose the values:
```
[
  "CANCEL_SUBSCRIPTION",
  "CHANGE_SUBSCRIPTION",
  "COMPLAINT",
  "OTHER"
]
```

#### Result
A temporary variable `result` that contains a result JSON object with a field `decision` containing the final decision and a field `reasoning` containing an explanation of the reasoning behind the decision. Can be mapped to one or more process variables using the result expression.

---

### ✍🏼 Compose Connector

Can compose text like e-mails or letters based on multiple input variables and store the result text in an output variable.

#### Configuration

Configure a desired style, tone and language for the text and describe what it should cover. Give a sender name (e.g. company name) that will be used in the complimentary close. The recipient should be obvious from the contents of the input variables.

#### Result
A temporary variable `result` that directly contains the result text. Can be mapped to a process variables using the result expression.

---

### 🌍 Translate Connector

Can translate multiple input variables to any given language and store the result in one or more output variables

#### Configuration

Enter the target language (e.g. `English`).

#### Result
A temporary variable `result` that contains a result JSON object with a field for every input field, containing the translation. Can be mapped to one or more process variables using the result expression.

---

### 🪄 Generic Connector

Can execute custom tasks not covered by the specialized connectors.

#### Configuration

Describe the task:

```
Perform task X and store the result in the result field. Also describe the reasoning behind your result.
```

Specify the output schema:

```
{
  result: "the result of the task",
  reasoning: "the reasoning behind the task result"
}
```
#### Result
A temporary variable `result` that contains a result JSON object as specified in the output schema. Can be mapped to one or more process variables using the result expression.

---

#### Element Templates

The element templates can be found under [element-templates](element-templates).



## Project Setup

### Build

You can package the Connectors by running the following command:

```bash
mvn clean package
```

This will create the following artifacts:

- A thin JAR without dependencies.
- An uber JAR containing all dependencies, potentially shaded to avoid classpath conflicts. This will not include the SDK artifacts since those are in scope `provided` and will be brought along by the respective Connector Runtime executing the Connectors.

### Configuration

In order to run, the connectors will require some basic setup, including an API key to OpenAI and connection details to connect to Camunda 8 platform.
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

If you want to connect to Camunda 8 Cloud, please use the following configuration (independently from run mode); 
```
OPENAI_API_KEY=<put your key here>
ZEEBE_CLIENT_CLOUD_CLUSTER-ID=<cluster-id>
ZEEBE_CLIENT_CLOUD_CLIENT-ID=<client-id>
ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=<client-secret>
ZEEBE_CLIENT_CLOUD_REGION=bru-2
```

### Test with local runtime

The [Camunda Connector Runtime](https://github.com/camunda-community-hub/spring-zeebe/tree/master/connector-runtime#building-connector-runtime-bundles) 
is included on the test scope to run your function as a local Java application.

In your IDE you can also simply navigate to the `LocalContainerRuntime` class in test scope and run it via your IDE.
Please include the values from the configuration block as environment variables of your runtime either by copying the
values manually or using the [EnvFile Plugin for IntelliJ](https://plugins.jetbrains.com/plugin/7861-envfile).

### Run Zeebe Cluster locally

In order to start a local Zeebe cluster please run:

```bash 
docker compose up -d
```

### Run Connector locally

In order to start a local connector runtime please run:

```bash 
docker compose --profile connector up -d
```

## License

This library is developed under

[![Apache 2.0 License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](/LICENSE)

## Sponsors and Customers

[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-red.svg)](https://holisticon.de/)
