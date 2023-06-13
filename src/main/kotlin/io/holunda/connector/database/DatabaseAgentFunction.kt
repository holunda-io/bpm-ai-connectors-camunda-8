package io.holunda.connector.database

import com.aallam.openai.api.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import io.holunda.connector.openapi.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
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

    val result = LangchainClient().run("database", Json.encodeToString(
      DatabaseAgentTask(
        request.model.modelId.id,
        request.taskDescription,
        request.inputJson,
        request.databaseUrl,
        request.outputSchema
      ))
    )

    val json = result.toMap()

    logger.info("DatabaseAgentFunction result: $json")

    return DatabaseAgentResult(json)
  }

  @Serializable
  data class DatabaseAgentTask(
    val model: String,
    val task: String,
    val context: String,
    val databaseUrl: String,
    val outputSchema: String
  )

  companion object : KLogging()
}
