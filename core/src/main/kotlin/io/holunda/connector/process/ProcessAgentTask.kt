package io.holunda.connector.process

import com.fasterxml.jackson.databind.*

data class ProcessAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val activities: Map<String, String>,
) {
    companion object {
        fun fromRequest(request: ProcessAgentRequest) =
            ProcessAgentTask(
                request.model.modelId,
                request.taskDescription,
                request.inputJson,
                request.activities.mapValues { it.value.description }
            )
    }
}
