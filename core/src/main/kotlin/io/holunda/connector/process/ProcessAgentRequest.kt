package io.holunda.connector.process

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class ProcessAgentRequest(
  val inputJson: JsonNode,
  val taskDescription: String,
  val activities: Map<String, ActivityDefinition>,
  val model: Model,

  @Secret
  var apiKey: String
)
