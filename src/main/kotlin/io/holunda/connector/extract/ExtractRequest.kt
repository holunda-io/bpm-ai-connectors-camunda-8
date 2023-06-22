package io.holunda.connector.extract

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*

data class ExtractDataRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val inputJson: String,
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val extractionJson: String,
    val mode: Mode,
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
