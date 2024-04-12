# Getting Started
## General Configuration

### Input Variables

Most connectors base their work on a map of input variables given as a FEEL context/map, e.g.:
```
{ "myVariable": myVariable }
```
The keys of the map should be the name of the variable or another fitting label for the variable content, as this will give the model context.

For example, if you input a variable containing the subject of an email, the label should make that clear: `"emailSubject":`. Otherwise, (if you name it `"var3"` for example) it might be hard for the model to correctly interpret the data.

### Model

By default, all connectors will use the `OpenAI GPT-4 Turbo` model. This model is very capable and can natively work with images. 
We also see very similar performance using `Anthropic Claude 3 Opus`, also natively supporting images. The best "bang for the buck" you will get from `Anthropic Claude 3 Haiku`, the fastest and cheapest model available and at the same time very capable for most tasks (also image enabled). 
`OpenAI GPT-3.5 Turbo` is not recommended for any task, given Haiku's superior performance and price point.

> [!TIP]
> For using 100% local, open-source/open-access models, see [here](local-models.md).

### Output Variable Mapping

To use the result of a connector, you must provide an output expression as a FEEL context. 

The result of a connector is always put in a local variable `result`. Depending on the connector type, this may be a context with additional fields or just a string value.

As the variable is local, you need to define which parts of the result you want to keep in which variables:
```
{ "resultVar": result }
```

The resulting JSON object is then *merged* into the current process variables (so in this example there will be a new or overwritten process variable `resultVar`).

### Secrets

When using passwords, keys or other sensitive information in connectors, it is a good practice to use secrets to not expose this data to the VCS or Operate.

Simply use a value `{{secrets.MY_SECRET}}` in the BPMN and make an environment variable `MY_SECRET` with corresponding value available to the connector runtime (e.g. by putting it in the .env and passing that as `env_file` in docker compose).

The connector runtime will replace the `{{secrets.MY_SECRET}}` with the actual value during runtime.

> [!IMPORTANT]
> Camunda out-of-the-box connectors need their secrets configured in Camunda Console, the bpm.ai connectors have their own runtime.

---

[⏩ Continue to Connector Details Documentation](base-connectors.md)