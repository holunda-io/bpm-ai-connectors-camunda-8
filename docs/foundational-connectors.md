# Foundational Connectors

## 🔍 Extract Connector

Can extract or deduce information from multiple input variables, potentially do simple conversions along the way, and store the result in one or more output variables.

### Configuration

Provide a map of new variables to extract from the input, with descriptions of what they should contain:
```
{
  firstname: "first name",
  lastname: "last name",
  language: "the language that the email body is written in, as ISO code"
}
```

### Result
A temporary variable `result` that contains a result JSON object of the same form as configured above. Can be mapped to one or more process variables using the result expression.

---

## ⚖ Decide Connector

Can make decisions based on multiple input variables and store the result decision and the reasoning behind it in output variables.

### Configuration

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

### Result
A temporary variable `result` that contains a result JSON object with a field `decision` containing the final decision and a field `reasoning` containing an explanation of the reasoning behind the decision. Can be mapped to one or more process variables using the result expression.

---

## ✍🏼 Compose Connector

Can compose text like e-mails or letters based on multiple input variables and store the result text in an output variable.

### Configuration

Configure a desired style, tone and language for the text and describe what it should cover. Give a sender name (e.g. company name) that will be used in the complimentary close. The recipient should be obvious from the contents of the input variables.

### Result
A temporary variable `result` that directly contains the result text. Can be mapped to a process variables using the result expression.

---

## 🌍 Translate Connector

Can translate multiple input variables to any given language and store the result in one or more output variables

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
