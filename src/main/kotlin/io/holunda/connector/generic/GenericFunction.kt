package io.holunda.connector.generic

import com.fasterxml.jackson.databind.*
import com.fasterxml.jackson.module.kotlin.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.translate.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-generic",
  inputVariables = ["inputJson", "taskDescription", "outputFormat", "model", "apiKey"],
  type = "gpt-generic"
)
class GenericFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    LOG.info("Executing GenericFunction")
    val connectorRequest = context.variables.readFromJson<GenericRequest>()
    LOG.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: GenericRequest): GenericResult {
    val result = LangchainClient.run("generic",
      GenericTask(
        request.model.modelId,
        request.inputJson,
        request.taskDescription,
        request.outputFormat
      )
    )

    LOG.info("GenericFunction result: $result")

    return GenericResult(result)
  }

  data class GenericTask(
    val model: String,
    val context: JsonNode,
    val instructions: String,
    val output_schema: JsonNode,
  )

  companion object {
    private val LOG = LoggerFactory.getLogger(GenericFunction::class.java)
  }
}
