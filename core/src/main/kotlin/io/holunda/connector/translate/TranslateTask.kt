package io.holunda.connector.translate

import com.fasterxml.jackson.databind.*

data class TranslateTask(
    val model: String,
    val input: JsonNode,
    val target_language: String,
) {
    companion object {
        fun fromRequest(request: TranslateRequest) =
            TranslateTask(
                request.model.modelId,
                request.inputJson,
                request.language
            )
    }
}
