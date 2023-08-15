package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.*

data class RetrievalTask(
    val model: String,
    val query: String,
    val database: String,
    val database_url: String,
    val embedding_provider: String,
    val embedding_model: String,
    val mode: String,
    val output_schema: JsonNode?,
) {
    companion object {
        fun fromRequest(request: RetrievalRequest) =
            RetrievalTask(
                request.model.modelId,
                request.query,
                request.database,
                request.databaseUrl,
                request.embeddingProvider,
                request.embeddingModel,
                request.mode,
                request.outputSchema
            )
    }
}
