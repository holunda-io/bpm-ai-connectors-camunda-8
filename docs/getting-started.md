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

By default, all connectors will use `OpenAI GPT-3.5 Turbo` model. This model is fine for many tasks and very cost-effective and fast.
If you see undesired behavior for a complex task you should try `OpenAI GPT-4 Turbo`, and fall back to the slower, more expensive but usually smarter `OpenAI GPT-4` (non-Turbo) if needed.

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