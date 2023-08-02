package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*
import io.holunda.connector.extract.*

data class OpenApiAgentRequest(
  val inputJson: JsonNode,
  val query: String,
  val specUrl: String,
  val skillStoreUrl: String?,
  val outputSchema: JsonNode,
  val model: Model,

  @Secret
  var apiKey: String
)
