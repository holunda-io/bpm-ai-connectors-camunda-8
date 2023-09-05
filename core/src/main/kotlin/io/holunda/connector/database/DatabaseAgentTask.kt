package io.holunda.connector.database

import com.fasterxml.jackson.databind.*

data class DatabaseAgentTask(
    val model: String,
    val task: String,
    val context: JsonNode,
    val database_url: String,
    val output_schema: JsonNode?,
    val skill_mode: String,
    val skill_store: String?,
    val skill_store_url: String?,
    val skill_store_password: String?,

) {
    companion object {
        fun fromRequest(request: DatabaseAgentRequest) =
            DatabaseAgentTask(
                request.model.modelId,
                request.query.query,
                request.inputJson,
                request.databaseUrl,
                request.query.outputSchema,
                request.advanced.skillMode,
                request.advanced.skillDatabase?.type,
                request.advanced.skillDatabase?.url,
                request.advanced.skillDatabase?.password
            )
    }
}
