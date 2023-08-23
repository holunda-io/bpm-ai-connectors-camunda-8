package io.holunda.connector.database

import com.fasterxml.jackson.databind.*

data class DatabaseAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val database_url: String,
    val output_schema: JsonNode?,
    val skill_store_url: String?,
) {
    companion object {
        fun fromRequest(request: DatabaseAgentRequest) =
            DatabaseAgentTask(
                request.model.modelId,
                request.query,
                request.inputJson,
                request.databaseUrl,
                request.outputSchema,
                request.skillStoreUrl
            )
    }
}
