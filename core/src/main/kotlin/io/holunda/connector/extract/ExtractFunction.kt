package io.holunda.connector.extract

import com.fasterxml.jackson.databind.*
import com.fasterxml.jackson.module.kotlin.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.compose.*
import io.holunda.connector.database.*
import org.apache.commons.text.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-extract",
  inputVariables = ["inputJson", "extractionJson", "missingDataBehavior", "mode", "entitiesDescription", "model"],
  type = "gpt-extract"
)
class ExtractFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    LOG.info("Executing ExtractDataFunction")
    val connectorRequest = context.variables.readFromJson<ExtractDataRequest>()
    //val connectorRequest = context.bindVariables(ExtractDataRequest::class.java)
    LOG.info("Request: {}", connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: ExtractDataRequest): ExtractResult {
    val result = LLMServiceClient.run(
      "extract",
        ExtractTask(
          request.model.modelId,
          request.inputJson,
          request.extractionJson,
          request.mode == Mode.REPEATED,
          request.entitiesDescription
        )
    )

    fun checkNode(node: JsonNode) {
      if (request.missingDataBehavior == MissingDataBehavior.ERROR && node.toMap().values.any { it == null }) {
        throw ConnectorException("MISSING_DATA", "One or more result values are null")
      }
    }

    when {
      result.isArray -> result.forEach(::checkNode)
      result.isObject -> checkNode(result)
      else -> throw IllegalArgumentException("The result must be a JSON object or a JSON array")
    }

    LOG.info("ExtractDataFunction result: $result")

    return ExtractResult(result)
  }

  data class ExtractTask(
    val model: String,
    val context: JsonNode,
    val extraction_schema: JsonNode,
    val repeated: Boolean,
    val repeated_description: String?,
  )

  companion object {
    private val LOG = LoggerFactory.getLogger(ExtractFunction::class.java)
  }
}
