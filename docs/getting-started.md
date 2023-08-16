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

By default, all connectors will use `OpenAI GPT-3.5 Turbo` model. This model is fine for most tasks and pretty cost-effective and fast.
If you see undesired behavior for a complex task you can try `OpenAI GPT-4` (if you have access to it).

The foundational connectors also support the best model from Aleph Alpha and Cohere, respectively. These models are still under evaluation, not all features may be available and model performance will generally be sub-par compared to OpenAI. 

For using custom or open-source models, see [here](custom-models.md).

### Output Variable Mapping

To use the result of a connector, you must provide an output expression as a FEEL context. 

The result of a connector is always put in a local variable `result`. Depending on the connector type, this may be a context with additional fields or just a string value.

As the variable is local, you need to define which parts of the result you want to keep in which variables:
```
{ "result": result }
```

The resulting JSON object is then *merged* into the current process variables (so in this example there will be a new or overwritten process variable `result`).
