package io.holunda.connector.decide

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class DecideRequest(
  val inputJson: JsonNode,
  val instructions: String,
  val outputType: DecisionOutputType,
  val possibleValues: List<Any>?,
  val model: Model,

  @Secret
    var apiKey: String
)

enum class DecisionOutputType(name: String) {
    BOOLEAN("Boolean"),
    INTEGER("Integer"),
    STRING("String")
}
