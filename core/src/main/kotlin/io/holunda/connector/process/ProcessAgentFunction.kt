package io.holunda.connector.process

import com.fasterxml.jackson.databind.*
import com.fasterxml.jackson.module.kotlin.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.compose.*
import io.holunda.connector.openapi.*
import mu.*
import org.apache.commons.text.*
import org.slf4j.*
import java.util.*


@OutboundConnector(
  name = "gpt-process",
  inputVariables = ["inputJson", "taskDescription", "activities", "model"],
  type = "io.holunda.connector.process:1"
)
class ProcessAgentFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing ProcessAgentFunction")
    val connectorRequest = context.variables.readFromJson<ProcessAgentRequest>()
    //val connectorRequest = context.bindVariables(ProcessAgentRequest::class.java)
    logger.info("Request: {}", connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: ProcessAgentRequest): ProcessAgentResult {
    val result = LLMServiceClient.run("process",
      ProcessAgentTask(
        request.model.modelId,
        request.taskDescription,
        request.inputJson,
        request.activities.mapValues { it.value.description }
      )
    )

    val elements = jacksonObjectMapper().treeToValue<List<Element>>(result.get("elements"))
    val flows = jacksonObjectMapper().treeToValue<List<Flow>>(result.get("flows"))

    val creator = ProcessModelCreator(request.activities)
    val processId = creator.createProcess(elements, flows)

    logger.info("ProcessAgentFunction result: $processId")

    return ProcessAgentResult(processId ?: "")
  }

  data class ProcessAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val activities: Map<String, String>,
  )

  companion object : KLogging()
}
