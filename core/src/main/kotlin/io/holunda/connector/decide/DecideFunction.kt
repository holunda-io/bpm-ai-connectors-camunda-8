package io.holunda.connector.decide

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.decide.DecisionOutputType.*
import io.holunda.connector.generic.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-decide",
  inputVariables = ["inputJson", "instructions", "outputType", "possibleValues", "model", "apiKey"],
  type = "gpt-decide"
)
class DecideFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    LOG.info("Executing DecideFunction")
    val request = context.variables.readFromJson<DecideRequest>()
    LOG.info("Request: {}", request)
    context.validate(request)
    context.replaceSecrets(request)
    return executeConnector(request)
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
