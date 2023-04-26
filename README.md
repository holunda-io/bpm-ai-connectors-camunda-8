# Camunda 8 GPT Connectors

Task specific connectors powered by OpenAI GPT large language models.

## API

### Input

```json
{
  "apiKey": "OpenAI API key",
  "model": "GPT_3|GPT_4|CUSTOM"
}
```

The OpenAI API key must be available in the runtime environment, e.g. by providing a [connector-secrets.txt](connector-secrets.txt) file to docker-compose via `env_file:`.

### Output

```json
{
  "result": {
    "myProperty": "....."
  }
}
```

### Error codes

| Code | Description |
| - | - |
| NULL | `Missing Data Behavior` in Extract Connector is set to `Throw Error` and GPT could not find all requested information. |


### Element Template

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

In order to run, the connectors will require some basic setup, including an API key to Open AI and connection details to connect to Camunda 8 platform.
All these settings should be performed using the file called `connector-secrets.txt` (check the sample file). 

If your connector runs locally from your host machine (command line or IDE) and connect to locally running Zeebe Cluster:
```
OPENAI_API_KEY=<put your key here>
CAMUNDA_OPERATE_CLIENT_URL=localhost:8080
ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=localhost:26500
ZEEBE_CLIENT_SECURITY_PLAINTEXT=true
```

If your connector runs using docker compose in together with Zeebe Cluster:
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