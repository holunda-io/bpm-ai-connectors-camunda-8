package io.holunda.connector.decide

import com.fasterxml.jackson.databind.*

data class DecideTask(
    val model: String,
    val context: JsonNode,
    val strategy: String?,
    val instructions: String,
    val output_type: String,
    val possible_values: List<Any>?
) {
    companion object {
        fun fromRequest(request: DecideRequest) =
            DecideTask(
                request.model.modelId,
                request.inputJson,
                request.strategy,
                request.instructions,
                request.outputType.lowercase(),
                request.possibleValues
            )
    }
}
