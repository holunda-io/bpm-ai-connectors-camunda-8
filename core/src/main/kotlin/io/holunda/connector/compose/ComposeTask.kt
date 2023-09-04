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
                request.properties.type,
                request.properties.style,
                request.properties.tone,
                request.properties.length,
                request.properties.language,
                request.properties.temperature,
                request.sender,
                when (request.alignment.constitutionalPrinciple) {
                    null, "none" -> null
                    "custom" -> request.alignment.customPrinciple
                    else -> request.alignment.constitutionalPrinciple
                }
            )
    }
}
