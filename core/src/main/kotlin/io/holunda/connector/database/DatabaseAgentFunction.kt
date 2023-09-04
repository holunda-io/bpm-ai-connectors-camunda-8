package io.holunda.connector.database

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-database",
    inputVariables = [
        "inputJson",
        "query",
        "databaseUrl",
        "outputSchema",
        "advanced",
        "model"
    ],
    type = "io.holunda:connector-database:1"
)
class DatabaseAgentFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing DatabaseAgentFunction")
        val connectorRequest = context.bindVariables(DatabaseAgentRequest::class.java)
        logger.info("DatabaseAgentFunction request: $connectorRequest")
        return executeRequest(DatabaseAgentTask.fromRequest(connectorRequest))
    }

    private fun executeRequest(databaseAgentTask: DatabaseAgentTask): DatabaseAgentResult {
        val result = LLMServiceClient.run("database", databaseAgentTask)
        logger.info("DatabaseAgentFunction result: $result")
        return DatabaseAgentResult(result)
    }

    companion object : KLogging()
}
