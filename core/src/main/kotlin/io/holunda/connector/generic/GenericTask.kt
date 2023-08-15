package io.holunda.connector.generic

import com.fasterxml.jackson.databind.*

data class GenericTask(
    val model: String,
    val context: JsonNode,
    val instructions: String,
    val output_schema: JsonNode,
) {
    companion object {
        fun fromRequest(request: GenericRequest) =
            GenericTask(
                request.model.modelId,
                request.inputJson,
                request.taskDescription,
                request.outputFormat
            )
    }
}
