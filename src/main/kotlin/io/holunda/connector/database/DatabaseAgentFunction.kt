package io.holunda.connector.database

import com.aallam.openai.api.*
import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.openapi.*
import mu.*
import org.slf4j.*
import java.util.*


@OutboundConnector(
  name = "gpt-database",
  inputVariables = ["inputJson", "taskDescription", "databaseUrl", "outputSchema", "missingDataBehavior", "model", "apiKey"],
  type = "gpt-database"
)
class DatabaseAgentFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing DatabaseAgentFunction")
    val connectorRequest = context.variables.readFromJson<DatabaseAgentRequest>()
    logger.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: DatabaseAgentRequest): DatabaseAgentResult {
    val result = LangchainClient.run("database",
      DatabaseAgentTask(
        request.model.modelId.id,
        request.taskDescription,
        request.inputJson,
        request.databaseUrl,
        request.outputSchema
      )
    )

    logger.info("DatabaseAgentFunction result: $result")

    return DatabaseAgentResult(result)
  }

  data class DatabaseAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val databaseUrl: String,
    val outputSchema: JsonNode
  )

  companion object : KLogging()
}
