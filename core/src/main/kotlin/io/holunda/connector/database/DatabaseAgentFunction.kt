package io.holunda.connector.database

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import mu.*

@OutboundConnector(
    name = "gpt-database",
    inputVariables = [
        "inputJson",
        "query",
        "databaseUrl",
        "outputSchema",
        "skillStoreUrl",
        "model"
    ],
    type = "io.holunda:connector-database:1"
)
class DatabaseAgentFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing DatabaseAgentFunction")
        val connectorRequest = context.variables.readFromJson<DatabaseAgentRequest>()
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
