package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.*

data class RetrievalTask(
    val model: String,
    val query: String,
    val database: String,
    val database_url: String,
    val password: String?,
    val embedding_provider: String,
    val embedding_model: String,
    val document_content_description: String?,
    val metadata_field_info: JsonNode?,
    val mode: String,
    val output_schema: JsonNode?,
    val parent_document_store: String?,
    val parent_document_store_url: String?,
    val parent_document_store_password: String?,
    val parent_document_store_namespace: String?,
    val parent_document_id_key: String?
) {
    companion object {
        fun fromRequest(request: RetrievalRequest) =
            RetrievalTask(
                request.model.modelId,
                request.query.query,
                request.database.type,
                request.database.url,
                request.database.password,
                request.database.embedding.provider,
                request.database.embedding.model,
                request.advanced.documentDescription,
                request.advanced.fieldMetadata,
                request.query.mode,
                request.query.outputSchema,
                request.advanced.parentDocumentStore.type,
                request.advanced.parentDocumentStore.url,
                request.advanced.parentDocumentStore.password,
                request.advanced.parentDocumentStore.namespace,
                request.advanced.parentDocumentStore.parentDocumentId,
            )
    }
}
