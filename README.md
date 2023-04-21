> A template for new C8 connectors.
>
> To use this template update the following resources to match the name of your connector:
>
> * [README](./README.md) (title, description)
> * [Element Template](./element-templates/template-connector.json)
> * [POM](./pom.xml) (artifact name, id, description)
> * [Connector Function](./src/main/java/io/camunda/connector/MyConnectorFunction.java) (rename, implement, update `OutboundConnector` annotation)
> * [Service Provider Interface (SPI)](./src/main/resources/META-INF/services/io.camunda.connector.api.ConnectorFunction#L1) (rename)
>
> ...and delete this hint.


# Connector Template

Camunda Connector Template

## Build

You can package the Connector by running the following command:

```bash
mvn clean package
```

This will create the following artifacts:

- A thin JAR without dependencies.
- An uber JAR containing all dependencies, potentially shaded to avoid classpath conflicts. This will not include the SDK artifacts since those are in scope `provided` and will be brought along by the respective Connector Runtime executing the Connector.

### Shading dependencies

You can use the `maven-shade-plugin` defined in the [Maven configuration](./pom.xml) to relocate common dependencies
that are used in other Connectors and the [Connector Runtime](https://github.com/camunda-community-hub/spring-zeebe/tree/master/connector-runtime#building-connector-runtime-bundles).
This helps avoiding classpath conflicts when the Connector is executed. 

Use the `relocations` configuration in the Maven Shade plugin to define the dependencies that should be shaded.
The [Maven Shade documentation](https://maven.apache.org/plugins/maven-shade-plugin/examples/class-relocation.html) 
provides more details on relocations.

## API

### Input

```json
{
  "token": ".....",
  "message": "....."
}
```

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
| FAIL | Message starts with 'fail' (ignoring case) |

## Test locally

Run unit tests

```bash
mvn clean verify
```

### Test with local runtime

Use the [Camunda Connector Runtime](https://github.com/camunda-community-hub/spring-zeebe/tree/master/connector-runtime#building-connector-runtime-bundles) to run your function as a local Java application.

In your IDE you can also simply navigate to the `LocalContainerRuntime` class in test scope and run it via your IDE.
If necessary, you can adjust `application.properties` in test scope.

## Element Template

The element templates can be found in the [element-templates/template-connector.json](element-templates/template-connector.json) file.
