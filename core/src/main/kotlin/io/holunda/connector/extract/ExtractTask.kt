package io.holunda.connector.extract

import com.fasterxml.jackson.databind.*

data class ExtractTask(
    val model: String,
    val context: JsonNode,
    val instructions: String?,
    val extraction_schema: JsonNode,
    val repeated: Boolean,
    val repeated_description: String?,
) {
    companion object {
        fun fromRequest(request: ExtractRequest) =
            ExtractTask(
                request.model.modelId,
                request.inputJson,
                request.instructions,
                request.extractionJson,
                request.mode == Mode.REPEATED,
                request.entitiesDescription
            )
    }
}
