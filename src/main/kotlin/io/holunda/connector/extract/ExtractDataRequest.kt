package io.holunda.connector.extract

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*

data class ExtractDataRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val inputJson: String,
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val extractionJson: String,
    val missingDataBehavior: MissingDataBehavior,
    val model: String,

    @Secret
    var apiKey: String
)

enum class MissingDataBehavior {
    NULL, EMPTY, ERROR
}