package io.holunda.connector.planner

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.openapi.*
import io.holunda.connector.planner.*
import mu.*
import org.slf4j.*
import java.util.*

@OutboundConnector(
  name = "gpt-planner",
  inputVariables = ["inputJson", "taskDescription", "tools", "model", "apiKey"],
  type = "gpt-planner"
)
class PlannerFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing PlannerFunction")
    val connectorRequest = context.variables.readFromJson<PlannerRequest>()
    logger.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: PlannerRequest): PlannerResult {
    val result = LLMServiceClient.run("planner", PlannerTask(
        request.model.modelId,
        request.taskDescription,
        request.inputJson,
        request.tools.toStringMap(),
      )
    )

    val plan = result.toStringList()

    logger.info("PlannerFunction result: $plan")

    return PlannerResult(
      Task(
        task = request.taskDescription,
        tools = request.tools.toStringMap(),
        plan = plan,
      )
    )
  }

  data class PlannerTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val tools: Map<String,String>
  )

  companion object : KLogging()
}
