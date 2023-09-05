package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class RetrievalRequest(
    val model: Model,
    val database: VectorDatabaseConfig,
    val query: QueryConfig,
    val advanced: AdvancedConfig
)

data class QueryConfig(
    val query: String,
    val outputType: String,
    val outputSchema: JsonNode?,
    val mode: String,
)

data class VectorDatabaseConfig(
    val type: String,
    val url: String,
    val password: String?,
    val embedding: EmbeddingConfig,
)

data class EmbeddingConfig(
    val provider: String,
    val model: String,
)

data class AdvancedConfig(
    val fieldMetadata: JsonNode?,
    val documentDescription: String?,
    val parentDocumentStore: ParentDocumentConfig,
)

data class ParentDocumentConfig(
    val type: String,
    val url: String?,
    val password: String?,
    val namespace: String?,
    val parentDocumentId: String?,
)
