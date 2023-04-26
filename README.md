## Camunda 8 GPT Connectors

Task specific connectors powered by OpenAI GPT large language models.

### Build

You can package the Connectors by running the following command:

```bash
mvn clean package
```

This will create the following artifacts:

- A thin JAR without dependencies.
- An uber JAR containing all dependencies, potentially shaded to avoid classpath conflicts. This will not include the SDK artifacts since those are in scope `provided` and will be brought along by the respective Connector Runtime executing the Connectors.

### API

#### Input

```json
{
  "apiKey": "OpenAI API key",
  "model": "GPT_3|GPT_4|CUSTOM"
}
```

The OpenAI API key must be available in the runtime environment, e.g. by providing a [connector-secrets.txt](connector-secrets.txt) file to docker-compose via `env_file:`.

#### Output

```json
{
  "result": {
    "myProperty": "....."
  }
}
```

#### Error codes

| Code | Description |
| - | - |
| NULL | `Missing Data Behavior` in Extract Connector is set to `Throw Error` and GPT could not find all requested information. |

#### Test with local runtime

Use the [Camunda Connector Runtime](https://github.com/camunda-community-hub/spring-zeebe/tree/master/connector-runtime#building-connector-runtime-bundles) to run your function as a local Java application.

In your IDE you can also simply navigate to the `LocalContainerRuntime` class in test scope and run it via your IDE.
If necessary, you can adjust `application.properties` in test scope.

### Element Template

The element templates can be found under [element-templates](element-templates).

## License

This library is developed under

[![Apache 2.0 License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](/LICENSE)

## Sponsors and Customers

[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-red.svg)](https://holisticon.de/)