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

### Result
A temporary variable `result` that contains the answer text or a result JSON object. Can be mapped to process variables using the result expression.

---

## 🗄 Database Connector

Answers questions and natural language queries over SQL databases. 

Given just a database connection string and a query, this connector automatically explores the relevant tables and table schemas of a SQL database and performs one or more database queries to answer the given question.

Example scenarios are:
- rapid process prototyping (implement a traditional worker later)
- adding background information to user tasks

### Configuration

#### SQL Database

| Property                     | Description                                 | Example                       |
|------------------------------|---------------------------------------------|-------------------------------|
| `Database Connection String` | The full connection string to a SQL databse | `postgresql://postgres:postgres@localhost:5438/postgres`                    |

#### Query

Provide a natural language query or question as a fully formed sentence.

Select Output Type `Natural Language Answer` to get back a natural language text that answers the given query.
Select `JSON` to provide a JSON-schema and receive back a JSON response (see Extract Connector in [Foundational Connectors](docs/foundational-connectors.md) for more details)


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