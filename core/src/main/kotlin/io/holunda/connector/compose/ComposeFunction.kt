package io.holunda.connector.compose

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.generic.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-compose",
  inputVariables = ["inputJson", "description", "type", "style", "tone", "length", "language", "sender", "customPrinciple", "constitutionalPrinciple", "model", "apiKey"],
  type = "gpt-compose"
)
class ComposeFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    LOG.info("Executing ComposeFunction")
    val connectorRequest = context.variables.readFromJson<ComposeRequest>()
    LOG.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: ComposeRequest): ComposeResult {
    val constitutionalPrinciple = when (request.constitutionalPrinciple) {
      null, "none" -> null
      "custom" -> request.customPrinciple
      else -> request.constitutionalPrinciple
    }

    val result = LLMServiceClient.run("compose",
      ComposeTask(
        request.model.modelId,
        request.inputJson,
        request.description,
        request.type,
        request.style,
        request.tone,
        request.length,
        request.language,
        request.sender,
        constitutionalPrinciple
      )
    )

    LOG.info("ComposeFunction result: $result")

    return ComposeResult(result)
  }

  data class ComposeTask(
    val model: String,
    val context: JsonNode,
    val instructions: String,
    val type: String,
    val style: String,
    val tone: String,
    val length: String,
    val language: String,
    val sender: String?,
    val constitutional_principle: String?,
  )

  companion object {
    private val LOG = LoggerFactory.getLogger(ComposeFunction::class.java)
  }
}
