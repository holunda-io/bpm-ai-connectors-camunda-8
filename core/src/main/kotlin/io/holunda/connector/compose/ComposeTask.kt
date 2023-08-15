package io.holunda.connector.compose

import com.fasterxml.jackson.databind.*

data class ComposeTask(
    val model: String,
    val context: JsonNode,
    val instructions: String,
    val type: String,
    val style: String,
    val tone: String,
    val length: String,
    val language: String,
    val temperature: Double,
    val sender: String?,
    val constitutional_principle: String?,
) {
    companion object {
        fun fromRequest(request: ComposeRequest) =
            ComposeTask(
                request.model.modelId,
                request.inputJson,
                request.description,
                request.type,
                request.style,
                request.tone,
                request.length,
                request.language,
                request.temperature,
                request.sender,
                when (request.constitutionalPrinciple) {
                    null, "none" -> null
                    "custom" -> request.customPrinciple
                    else -> request.constitutionalPrinciple
                }
            )
    }
}
