package io.holunda.connector.database

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.extract.*

data class DatabaseAgentRequest(
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val inputJson: String,
  val taskDescription: String,
  val databaseUrl: String,
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val outputSchema: String,
  val missingDataBehavior: MissingDataBehavior,
  val model: Model,

  @Secret
  var apiKey: String
)
