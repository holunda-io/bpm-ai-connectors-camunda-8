package io.holunda.connector.extract

import com.aallam.openai.api.*
import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import io.holunda.connector.database.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-extract",
  inputVariables = ["inputJson", "extractionJson", "missingDataBehavior", "mode", "entitiesDescription", "model", "apiKey"],
  type = "gpt-extract"
)
class ExtractFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    LOG.info("Executing ExtractDataFunction")
    val connectorRequest = context.variables.readFromJson<ExtractDataRequest>()
    LOG.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: ExtractDataRequest): ExtractResult {
    val result = LangchainClient().run(
      "extract", Json.encodeToString(
        ExtractTask(
          request.model.modelId.id,
          request.inputJson,
          Json.decodeFromString(request.extractionJson),
          request.mode == Mode.REPEATED,
          request.entitiesDescription
        )
      )
    )

    val rootNode = result.toJsonNode()

    fun checkNode(node: JsonNode) {
      if (request.missingDataBehavior == MissingDataBehavior.ERROR && node.toMap().values.any { it == null }) {
        throw ConnectorException("MISSING_DATA", "One or more result values are null")
      }
    }

    when {
      rootNode.isArray -> rootNode.forEach(::checkNode)
      rootNode.isObject -> checkNode(rootNode)
      else -> throw IllegalArgumentException("The result must be a JSON object or a JSON array")
    }

    LOG.info("ExtractDataFunction result: $result")

    return ExtractResult(rootNode)
  }

  @Serializable
  data class ExtractTask(
    val model: String,
    val context: String,
    val extraction_schema: JsonObject,
    val repeated: Boolean,
    val repeated_description: String?,
  )

  companion object {
    private val LOG = LoggerFactory.getLogger(ExtractFunction::class.java)
  }
}
