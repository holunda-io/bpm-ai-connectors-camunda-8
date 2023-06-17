package io.holunda.connector.planner

import com.aallam.openai.api.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import io.holunda.connector.openapi.*
import io.holunda.connector.planner.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
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
    val result = LangchainClient().run("planner", Json.encodeToString(
      PlannerTask(
        request.model.modelId.id,
        request.taskDescription,
        request.inputJson,
        request.tools.toStringMap(),
      )
    ))

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

  @Serializable
  data class PlannerTask(
    val model: String,
    val task: String,
    val context: String,
    val tools: Map<String,String>
  )

  companion object : KLogging()
}
