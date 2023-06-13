package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.extract.*

data class OpenApiAgentRequest(
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val inputJson: String,
  val taskDescription: String,
  val specUrl: String,
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val outputSchema: String,
  val missingDataBehavior: MissingDataBehavior,
  val model: Model,

  @Secret
  var apiKey: String
)
