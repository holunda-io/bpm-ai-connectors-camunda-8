package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.planner.*
import mu.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-openapi",
  inputVariables = ["inputJson", "taskDescription", "specUrl", "outputSchema", "missingDataBehavior", "model", "apiKey"],
  type = "gpt-openapi"
)
class OpenApiAgentFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing OpenApiAgentFunction")
    val connectorRequest = context.variables.readFromJson<OpenApiAgentRequest>()
    logger.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: OpenApiAgentRequest): OpenApiAgentResult {
    val result = LangchainClient.run("openapi",
      OpenApiAgentTask(
        request.model.modelId,
        request.taskDescription,
        request.inputJson,
        request.specUrl,
        request.outputSchema
      )
    )

    val json = result.toMap()

    logger.info("OpenApiAgentFunction result: $json")

    return OpenApiAgentResult(json)
  }

  data class OpenApiAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val specUrl: String,
    val outputSchema: JsonNode
  )

  companion object : KLogging()
}
