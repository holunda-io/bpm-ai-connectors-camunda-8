package io.holunda.connector.executor

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.compose.*
import mu.*
import org.apache.commons.text.*
import org.slf4j.*
import java.util.*


@OutboundConnector(
  name = "gpt-executor",
  inputVariables = ["inputJson", "taskObject", "result", "model"],
  type = "gpt-executor"
)
class ExecutorFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing ExecutorFunction")
    val connectorRequest = context.variables.readFromJson<ExecutorRequest>()
    //val connectorRequest = context.bindVariables(ExecutorRequest::class.java)
    logger.info("Request: {}", connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: ExecutorRequest): ExecutorResult {
    val task = if (request.result != null) {
      request.taskObject.copy(
        results = request.taskObject.results + listOf(request.result)
      )
    } else request.taskObject

    val previousStepsAndResults = task.pastSteps.zip(task.results).toString()
    val currentPlanStep = task.plan.getOrElse(task.results.size) { _ -> "" }

    val currentStep = LLMServiceClient.run("executor",
      ExecutorTask(
        request.model.modelId,
        task.task,
        request.inputJson,
        task.tools,
        previousStepsAndResults,
        currentPlanStep
      )
    ).toStringMap()

    val currentStepSummary = "${currentStep["action"]}: ${currentStep["input"]}"

    val updatedTask = task.copy(
      currentStep = currentStep,
      pastSteps = task.pastSteps + listOf(currentStepSummary)
    )

    logger.info("ExecutorFunction result: $updatedTask")

    return ExecutorResult(updatedTask)
  }

  data class ExecutorTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val tools: Map<String,String>,
    val previous_steps: String,
    val current_step: String
  )

  companion object : KLogging()
}
