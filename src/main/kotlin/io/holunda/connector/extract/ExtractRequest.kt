package io.holunda.connector.extract

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class ExtractDataRequest(
  val inputJson: JsonNode,
  val extractionJson: JsonNode,
  val mode: Mode,
  val entitiesDescription: String?,
  val missingDataBehavior: MissingDataBehavior,
  val model: Model,

  @Secret
    var apiKey: String
)

enum class Mode {
  SINGLE, REPEATED
}

enum class MissingDataBehavior {
    NULL, ERROR
}
