package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.compose.*
import io.holunda.connector.planner.*
import mu.*
import org.apache.commons.text.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-openapi",
  inputVariables = ["inputJson", "taskDescription", "specUrl", "outputSchema", "skillStoreUrl", "model"],
  type = "gpt-openapi"
)
class OpenApiAgentFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing OpenApiAgentFunction")
    val connectorRequest = context.variables.readFromJson<OpenApiAgentRequest>()
    //val connectorRequest = context.bindVariables(OpenApiAgentRequest::class.java)
    logger.info("Request: {}", connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: OpenApiAgentRequest): OpenApiAgentResult {
    val result = LLMServiceClient.run("openapi",
      OpenApiAgentTask(
        request.model.modelId,
        request.query,
        request.inputJson,
        request.specUrl,
        request.outputSchema,
        request.skillStoreUrl
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
    val spec_url: String,
    val output_schema: JsonNode,
    val skill_store_url: String?,
  )

  companion object : KLogging()
}
