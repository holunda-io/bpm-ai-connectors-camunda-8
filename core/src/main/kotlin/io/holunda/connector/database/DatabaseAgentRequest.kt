package io.holunda.connector.database

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*
import io.holunda.connector.extract.*

data class DatabaseAgentRequest(
  val inputJson: JsonNode,
  val taskDescription: String,
  val databaseUrl: String,
  val skillStoreUrl: String?,
  val outputSchema: JsonNode,
  val missingDataBehavior: MissingDataBehavior,
  val model: Model,

  @Secret
  var apiKey: String
)
