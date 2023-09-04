package io.holunda.connector.executor

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-executor",
    inputVariables = [
        "inputJson",
        "taskObject",
        "result",
        "model"
    ],
    type = "io.holunda:connector-executor:1"
)
class ExecutorFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing ExecutorFunction")
        val connectorRequest = context.bindVariables(ExecutorRequest::class.java)
        logger.info("ExecutorFunction request: $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: ExecutorRequest): ExecutorResult {
        val task = if (request.result != null) {
            request.taskObject.copy(
                results = request.taskObject.results + listOf(request.result)
            )
        } else request.taskObject

        val currentStep = LLMServiceClient.run(
            "executor",
            ExecutorTask.fromRequestAndTaskObject(request, task)
        ).toStringMap()

        val currentStepSummary = "${currentStep["action"]}: ${currentStep["input"]}"

        val updatedTask = task.copy(
            currentStep = currentStep,
            pastSteps = task.pastSteps + listOf(currentStepSummary)
        )

        logger.info("ExecutorFunction result: $updatedTask")

        return ExecutorResult(updatedTask)
    }

    companion object : KLogging()
}
