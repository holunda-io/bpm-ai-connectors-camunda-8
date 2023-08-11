package io.holunda.connector.generic

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class GenericRequest(
  val inputJson: JsonNode,
  val outputFormat: JsonNode,
  val taskDescription: String,
  val model: Model
)
