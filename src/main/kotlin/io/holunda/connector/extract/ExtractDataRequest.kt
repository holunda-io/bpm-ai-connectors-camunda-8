package io.holunda.connector.extract

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*

data class ExtractDataRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var inputJson: String? = null,

    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var extractionJson: String? = null,

    var missingDataBehavior: MissingDataBehavior? = null,

    var model: String? = null,

    @Secret
    var apiKey: String? = null
)

enum class MissingDataBehavior {
    NULL, EMPTY, ERROR
}