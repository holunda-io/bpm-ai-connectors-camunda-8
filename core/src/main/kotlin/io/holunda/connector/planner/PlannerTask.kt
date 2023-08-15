package io.holunda.connector.planner

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class PlannerTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val tools: Map<String, String>
) {
    companion object {
        fun fromRequest(request: PlannerRequest) =
            PlannerTask(
                request.model.modelId,
                request.taskDescription,
                request.inputJson,
                request.tools.toStringMap(),
            )
    }
}
