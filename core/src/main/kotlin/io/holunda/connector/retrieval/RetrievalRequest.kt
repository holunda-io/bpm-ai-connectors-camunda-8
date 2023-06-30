package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*
import io.holunda.connector.extract.*

data class RetrievalRequest(
  val query: String,
  val databaseUrl: String,
  val embeddingProvider: String,
  val embeddingModel: String,
  val model: Model,

  @Secret
  var apiKey: String
)
