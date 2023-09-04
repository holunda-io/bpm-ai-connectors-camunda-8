package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.*

data class OpenApiAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val spec_url: String,
    val output_schema: JsonNode?,
    val skill_mode: String,
    val skill_store: String?,
    val skill_store_url: String?,
    val skill_store_password: String?,
) {
    companion object {
        fun fromRequest(request: OpenApiAgentRequest) =
            OpenApiAgentTask(
                request.model.modelId,
                request.query,
                request.inputJson,
                request.specUrl,
                request.outputSchema,
                request.advanced.skillMode,
                request.advanced.skillDatabase?.type,
                request.advanced.skillDatabase?.url,
                request.advanced.skillDatabase?.password
            )
    }
}
