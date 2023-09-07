# Agentic Connectors

* [📄 Q&A Retrieval Connector](#-qa-retrieval-connector)
* [🗄 Database Connector](#-decide-connector)
* [🌐 OpenAPI REST Connector](#-compose-connector)
* [👷 Process Generation Connector](#-translate-connector)
* [✅ Plan & Execute Connectors](#-generic-connector)

## What does "agentic" mean?

"Agentic" in the context of this project refers to a special kind of connectors that are not "single-pass" and don't work following a fixed, pre-defined procedure. Instead, in these connectors, the LLM:
- has access to a set of tools (or actions) that it can use to solve the task
- dynamically uses the tools as it sees fit
- decides for itself when the task is complete or if it needs additional steps

Tools in these connectors usually give the model a way to interact with another system (like a database or API). 
And it gives the model the freedom to act on these tools as necessary to solve the task, without many restrictions.

This makes these connectors very dynamic and adaptive in the kinds of tasks they can solve, basically simulating a human worker.

On the flip-side, this approach is challenging for even the most capable models today (this is why we limit model selection to OpenAI models and strongly recommend GPT-4). **Mileage will vary depending on the given task.** Some results surprise, but others may disappoint. **In no way is this mode of operation reliable or predictable!**

## 📄 Q&A Retrieval Connector

Answers questions over documents indexed in a vector database.

Given a vector database with an index of document chunks (e.g. from PDFs, websites, Wikis, Confluence, ...), this connector first retrieves relevant chunks using semantic search based on a specified text embedding model (must match the embedding used for indexing).
The retrieved documents are then used as context to answer the given question.

Since the retrieval step is an agent tool, the connector can perform multiple successive queries e.g. to answer complex questions with multiple aspects or comparisons.

Example scenarios are:
- automatic customer service question answering
- adding background information to user tasks based on company knowledge bases

### Configuration

#### Vector Database

| Property              | Description                                                    | Example                       |
|-----------------------|----------------------------------------------------------------|-------------------------------|
| `Vector Database`     | The type of Vector Database to use                             | `Weaviate`                    |
| `Vector Database URL` | Database connection string                                     | `http://localhost:8080/index` |
| `Embedding Provider`  | Provider of the text embedding model used for indexed data     | `OpenAI`                      |
| `Embedding Model`     | Text embedding model from above provider used for indexed data | `text-embedding-ada-002`      |

#### Query

Provide a natural language query or question as a fully formed sentence.

Select Output Type `Natural Language Answer` to get back a natural language text that answers the given query. 
Select `JSON` to provide a JSON-schema and receive back a JSON response (see Extract Connector in [Foundational Connectors](docs/foundational-connectors.md) for more details)

#### Advanced

For more advanced retrieval, the connector supports filtering on metadata and decoupling retrieved chunks from the vector database and (usually larger) chunks used for answer synthesis.

###### Metadata filtering
The LLM can automatically derive filters from the query to narrow down search to relevant document chunks in a large and diverse index.

For this, you can provide a brief description of the documents in your index (optional) and define a list of schemas for the metadata fields you want to filter on, e.g.:
```
[
  {
    name: "bike_make",
    description: "The bike make.",
    type: "string",
    enum: ["Sun Bicycles", "Cowboy"]
  },
  {
    name: "bike_model",
    description: "The bike model.",
    type: "string",
    enum: ["Electrolite", "3"]
  }
]
```

The `enum` field is optional but a good idea if the possible values are not obvious and not too many. If the model chooses a non-matching filter value, it may not retrieve any documents and will not be able to return an answer.

###### Parent Documents

The text chunks used for retrieval with the vector database are often not well-suited to also be used for generating the answer.

This is because the embedding is more accurate for smaller chunks ("lost-in-the-middle" problem) while the answer synthesis needs appropriate context and suffers from too many small, unordered chunks. In addition, you may want to also index secondary data like summaries or hypothetical questions to enhance retrieval recall.

To enable theses use-cases, you can configure a "parent ID" field that should be present in all chunks in the vector database. These IDs should point to the respective parent document (or larger chunk) suitable for answer synthesis (make sure the parent documents are not too large, the connector will use up to 4 parent documents at once for answer synthesis).
Also configure a document key-value store from which the parent documents can be fetched by ID.

### Result
A temporary variable `result` that contains the answer text in `result.answer` (in the future there will probably be a `result.sources` field that contains references to source documents) or a result JSON object. Can be mapped to process variables using the result expression.

---

## 🗄 Database Connector

Answers questions and natural language queries over SQL databases. 

Given just a database connection string and a query, this connector automatically explores the relevant tables and table schemas of a SQL database and performs one or more database queries to answer the given question.

Example scenarios are:
- rapid process prototyping (implement a traditional worker later)
- adding background information to user tasks

NOTE: You should use a read-only database user.

### Configuration

#### SQL Database

| Property                     | Description                                 | Example                       |
|------------------------------|---------------------------------------------|-------------------------------|
| `Database Connection String` | The full connection string to a SQL databse | `postgresql://postgres:postgres@localhost:5438/postgres`                    |

#### Query

Provide a natural language query or question as a fully formed sentence.

Select Output Type `Natural Language Answer` to get back a natural language text that answers the given query.
Select `JSON` to provide a JSON-schema and receive back a JSON response (see Extract Connector in [Foundational Connectors](docs/foundational-connectors.md) for more details)

#### Advanced / Skill Library

Internally, the Database Connector generates Python code snippets. This code can optionally be stored and re-used, effectively building a library of learned "skills" that the connector already knows how to solve.

This enables two exciting use-cases:

###### Skill Library (Preview)

If enabled, the connector can create and use skill functions from a previous run by fetching relevant snippets from a vector database. 
An LLM is used to judge whether a snippet is actually a correct and successful solution to the given problem and only then create a new skill. 
If a solution snippet simply delegates to another basic or skill function, no skill is created.

Using a skill library allows the connector to solve increasingly complex problems through composition and save resources for common problems. 
Theoretically, it is also possible to add handwritten solutions for typical or difficult problems.

To enable, select a mode (only using existing skills or also creating new skills if possible) and configure a vector database. 
The connector will automatically create an index.

###### Direct Calling (Future Release)

If the connector is executing a second time with the same input variables (but possibly different values), stored code from the previous run can directly be called with the new variable value assignments and directly yield a result - bypassing the LLM to save time and money.

This is like a worker that self-implements on first run. Write once, run a million times for free :)

NOTE: For this to work, your variable values need to be "pre-processed" and not contain e.g. any unstructured data. The variable values need to be directly usable from code. Simple and obvious transformations that are easy to do in code are ok, but it is better to e.g. have a `firstname` and `lastname` instead of a composite `name` which could lead to surprises when trying to split it up.

### Result
A temporary variable `result` that contains the answer text or a result JSON object. Can be mapped to process variables using the result expression.

---

## 🌐 OpenAPI REST Connector

Performs tasks and answers questions using a REST API.

### Configuration

#### OpenAPI Spec

| Property             | Description                          | Example                              |
|----------------------|--------------------------------------|--------------------------------------|
| `OpenAPI 3 Spec URL` | URL to a OpenAPI version 3 JSON spec | `http://localhost:8080/openapi.json` |

#### Task

Provide a natural language task or query as a fully formed sentence.

Provide a JSON-schema for the output (see Extract Connector in [Foundational Connectors](docs/foundational-connectors.md) for more details)

#### Advanced / Skill Library

Internally, the OpenAPI Connector generates Python code snippets. This code can optionally be stored and re-used, effectively building a library of learned "skills" that the connector already knows how to solve.

This enables two exciting use-cases:

###### Skill Library (Preview)

If enabled, the connector can create and use skill functions from a previous run by fetching relevant snippets from a vector database.
An LLM is used to judge whether a snippet is actually a correct and successful solution to the given problem and only then create a new skill.
If a solution snippet simply delegates to another basic or skill function, no skill is created.

Using a skill library allows the connector to solve increasingly complex problems through composition and save resources for common problems.
Theoretically, it is also possible to add handwritten solutions for typical or difficult problems.

To enable, select a mode (only using existing skills or also creating new skills if possible) and configure a vector database.
The connector will automatically create an index.

###### Direct Calling (Future Release)

If the connector is executing a second time with the same input variables (but possibly different values), stored code from the previous run can directly be called with the new variable value assignments and directly yield a result - bypassing the LLM to save time and money.

This is like a worker that self-implements on first run. Write once, run a million times for free :)

NOTE: For this to work, your variable values need to be "pre-processed" and not contain e.g. any unstructured data. The variable values need to be directly usable from code. Simple and obvious transformations that are easy to do in code are ok, but it is better to e.g. have a `firstname` and `lastname` instead of a composite `name` which could lead to surprises when trying to split it up.


### Result
A temporary variable `result` that contains a result JSON object. Can be mapped to process variables using the result expression.

---

## 👷 Process Generation Connector

Generates and deploys a fully executable BPMN process to solve the given task using a set of given activities (e.g. our Database/OpenAPI/Retrieval connectors or User Tasks).

Automatically configures input and output variable mappings, task instructions/queries, and output schemas.

---

## ✅ Plan & Execute Connectors

The Planner Connector outputs a high level step-by-step plan for a given task. The Execute Connector takes the plan, the current step and previous results to output a new current step that can be used in a gateway to execute the next activity in a process.

---