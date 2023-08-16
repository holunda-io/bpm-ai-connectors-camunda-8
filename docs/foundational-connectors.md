# Foundational Connectors

* [🔍 Extract Connector](#-extract-connector)
* [⚖ Decide Connector](#-decide-connector)
* [✍🏼 Compose Connector](#-compose-connector)
* [🌍 Translate Connector](#-translate-connector)
* [🪄 Generic Connector](#-generic-connector)

## 🔍 Extract Connector

Extracts information from structured or unstructured data in multiple input variables, potentially doing simple conversions along the way, and stores the result in one or more output variables.

### Configuration

Provide a JSON object schema of the structure to extract from the input, with descriptions of what they should contain:
```
{
  product: {
      description: "The name of the product",
      type: "string"
  },
  price: {
      description: "The price of the product",
      type: "number"
  },
  tags: {
      description: "Tags for the product",
      type: "array",
      items: {
        type: "string",
        description: "A product tag",
        enum: ["A", "B", "C"]
      }
    }
}
```

The following types are supported:
* string
* integer
* number
* boolean
* object
* array

You should always provide a **speaking name and description** and be aware that both are essentially part of the prompt engineering and determine how well the information is extracted.

As seen above, you can provide an enum array if all possible values are known.

Since extracting string values is very common, there is a shorthand:

```
{
  firstname: "first name",
  lastname: "last name"
}
```

This is equivalent to:

```
{
  firstname: {
      description: "first name",
      type: "string"
  },
  lastname: {
      description: "last name",
      type: "string"
  }
}
```

#### Extract a list of entities

Select Extraction Mode `Multiple Entities` to extract a list of multiple entity objects, each conforming to the configured schema.
You can provide an optional description for the entities to extract. 

The result will be a list of objects or an empty list.

### Result
A temporary variable `result` that contains a result JSON object of the same form as configured above. Can be mapped to one or more process variables using the result expression.

---

## ⚖ Decide Connector

Makes decisions based on multiple input variables and stores the result decision and the reasoning behind it in output variables.

### Configuration

Provide a natural language description of what the connector should decide, e.g.:
```
Decide what the intention of the customer's mail is.
```
Next, select the Output Type (`Boolean`, `Integer` or `String`).
If not `Boolean`, you may restrict the connector to a classification on a finite set of options, instead of letting it freely choose the result value:
```
[
  "CANCEL_SUBSCRIPTION",
  "CHANGE_SUBSCRIPTION",
  "COMPLAINT",
  "OTHER"
]
```

### Result
A temporary variable `result` that contains a result JSON object with a field `decision` containing the final decision and a field `reasoning` containing an explanation of the reasoning behind the decision. Can be mapped to one or more process variables using the result expression.

---

## ✍🏼 Compose Connector

Composes texts for emails, letters, chat messages, or social media posts based on multiple input variables and stores the result text in an output variable.

### Configuration
#### General Properties
Configure a desired text type, style, tone, language, and length for the text.

#### Variance

Select a Variance value (controls model temperature). `None` will make the output mostly deterministic and more focused. 
The higher the variance, the more diverse and unpredictable the text becomes. A higher value is a good fit for creating creative content that should change on every run. Select `None` if you want to be as precise as possible and don't need diverse outputs.

#### Template

Select `No Template` to give a description on what the text should cover. Give a sender name (e.g. company name) that will be used in the complimentary close. The recipient should be obvious from the contents of the input variables or the description.

Select `Hybrid AI Template` to provide a text template. The template dictates the shape of the result text. You can use template variables using curly braces. Variables that are present in the input variable mapping are replaced directly, without going through the model. The remaining template variables will be filled in by the LLM. You can use simple variable names if obvious enough, or write full sentences with instructions on what to fill in. The result text is the template with all variables replaced or filled in.

The template is especially helpful to dictate a certain order and presence of text parts/contents, and to guarantee a certain pre-defined structure. 

Example:

```
Hello {name},

{ thank the customer for his purchase }

Yours,
{agentName}
```

Here `name` and `agentName` could be input variables, while the middle part would be generated. `name` and `agentName` will not be sent to the model in any way (be careful that the template variable names correctly match the input variable names). Whitespaces at the beginning and end of a variable are ignored and therefore optional.

#### Alignment

When generated text should be used directly without human control, it can make sense to add a safety layer that ensures appropriate output.

Select an Alignment Principle according to your needs. After generating the preliminary result text, another model will inspect the result with respect to the principle and potentially re-write parts of the text to satisfy the principle.
There is a set of pre-defined principles available, or select `Custom` to write a custom principle, e.g.:

```
The text must not contain any offensive or rude language. It should always be polite and professional.
```

Using this alignment technique, it is generally very unlikely (but not impossible) that a result text will violate the principle, if written correctly.

Note that alignment adds token/time overhead and that the OpenAI models are generally already very unlikely to output offensive text, if not provoked. So making sure that a user has no direct or indirect path to influence the text generation is usually enough to obtain safe text.

### Result
A temporary variable `result` that directly contains the result text. Can be mapped to a process variable using the result expression.

---

## 🌍 Translate Connector

Translates multiple input variables to any given language and stores the result in one or more output variables

### Configuration

Enter the target language (e.g. `English`).

### Result
A temporary variable `result` that contains a result JSON object with a field for every input field, containing the translation. Can be mapped to one or more process variables using the result expression.

---

## 🪄 Generic Connector

Can execute custom tasks not covered by the specialized connectors.

### Configuration

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
### Result
A temporary variable `result` that contains a result JSON object as specified in the output schema. Can be mapped to one or more process variables using the result expression.
