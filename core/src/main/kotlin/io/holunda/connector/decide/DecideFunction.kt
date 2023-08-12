package io.holunda.connector.decide

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.compose.*
import io.holunda.connector.decide.DecisionOutputType.*
import io.holunda.connector.generic.*
import org.apache.commons.text.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-decide",
  inputVariables = ["inputJson", "instructions", "outputType", "possibleValues", "model"],
  type = "gpt-decide"
)
class DecideFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    LOG.info("Executing DecideFunction")
    val connectorRequest = context.variables.readFromJson<DecideRequest>()
    //val connectorRequest = context.bindVariables(DecideRequest::class.java)
    LOG.info("Request: {}", connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: DecideRequest): DecideResult {
    val result = LLMServiceClient.run("decide",
      DecideTask(
        request.model.modelId,
        request.inputJson,
        request.instructions,
        request.outputType.name.lowercase(),
        request.possibleValues
      )
    )

    LOG.info("DecideFunction result: $result")

    return DecideResult(result)
  }

  data class DecideTask(
    val model: String,
    val context: JsonNode,
    val instructions: String,
    val output_type: String,
    val possible_values: List<Any>?
  )

  companion object {
    private val LOG = LoggerFactory.getLogger(DecideFunction::class.java)
  }
}
