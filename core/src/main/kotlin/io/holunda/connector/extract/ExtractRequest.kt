package io.holunda.connector.extract

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class ExtractDataRequest(
  val inputJson: JsonNode,
  val extractionJson: JsonNode,
  val mode: Mode,
  val entitiesDescription: String?,
  val missingDataBehavior: MissingDataBehavior,
  val model: Model
)

enum class Mode {
  SINGLE, REPEATED
}

enum class MissingDataBehavior {
    NULL, ERROR
}
