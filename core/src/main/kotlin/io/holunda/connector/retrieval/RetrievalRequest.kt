package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.JsonNode
import io.holunda.connector.common.*

data class RetrievalRequest(
  val query: String,
  val database: String,
  val databaseUrl: String,
  val embeddingProvider: String,
  val embeddingModel: String,
  val mode: String,
  val outputSchema: JsonNode?,
  val model: Model
)
