package io.holunda.connector.compose

import com.aallam.openai.api.*
import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.generic.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-compose",
  inputVariables = ["inputJson", "description", "style", "tone", "language", "sender", "model", "apiKey"],
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
    val result = LangchainClient.run("compose",
      ComposeTask(
        request.model.modelId.id,
        request.inputJson,
        request.description,
        request.style,
        request.tone,
        request.language,
        request.sender
      )
    )

    LOG.info("ComposeFunction result: $result")

    return ComposeResult(result)
  }

  data class ComposeTask(
    val model: String,
    val context: JsonNode,
    val instructions: String,
    val style: String,
    val tone: String,
    val language: String,
    val sender: String,
  )

  companion object {
    private val LOG = LoggerFactory.getLogger(ComposeFunction::class.java)
  }
}
