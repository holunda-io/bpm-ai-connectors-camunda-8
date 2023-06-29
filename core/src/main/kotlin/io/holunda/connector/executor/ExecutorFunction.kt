package io.holunda.connector.executor

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import mu.*
import org.slf4j.*
import java.util.*


@OutboundConnector(
  name = "gpt-executor",
  inputVariables = ["inputJson", "task", "model", "apiKey"],
  type = "gpt-executor"
)
class ExecutorFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing ExecutorFunction")
    val connectorRequest = context.variables.readFromJson<ExecutorRequest>()
    logger.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: ExecutorRequest): ExecutorResult {
    val previousStepsAndResults = request.task.pastSteps.zip(request.task.results).toString()
    val currentPlanStep = request.task.plan.getOrElse(request.task.results.size) { _ -> "" }

    val req = ExecutorTask(
        request.model.modelId,
        request.task.task,
        request.inputJson,
        request.task.tools,
        previousStepsAndResults,
        currentPlanStep
    )
    logger.info("ExecutorFunction request: $req")
    val result = LangchainClient.run("executor", req)

    val currentStep = result.toStringMap()
    val currentStepSummary = currentStep["action"] + ": " + currentStep["input"]

    val updatedTask = request.task.copy(
      currentStep = currentStep,
      pastSteps = request.task.pastSteps + listOf(currentStepSummary)
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
