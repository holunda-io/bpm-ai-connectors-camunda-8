package io.holunda.connector.executor

import com.fasterxml.jackson.databind.*
import io.holunda.connector.planner.*

data class ExecutorTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val tools: Map<String, String>,
    val previous_steps: String,
    val current_step: String
) {
    companion object {
        fun fromRequestAndTaskObject(request: ExecutorRequest, task: Task): ExecutorTask {
            val previousStepsAndResults = task.pastSteps.zip(task.results).toString()
            val currentPlanStep = task.plan.getOrElse(task.results.size) { _ -> "" }
            return ExecutorTask(
                request.model.modelId,
                task.task,
                request.inputJson,
                task.tools,
                previousStepsAndResults,
                currentPlanStep
            )
        }
    }
}
