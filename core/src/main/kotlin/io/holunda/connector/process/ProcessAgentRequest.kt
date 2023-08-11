package io.holunda.connector.process

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class ProcessAgentRequest(
  val inputJson: JsonNode,
  val taskDescription: String,
  val activities: Map<String, ActivityDefinition>,
  val model: Model
)
