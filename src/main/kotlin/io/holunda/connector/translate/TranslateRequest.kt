package io.holunda.connector.translate

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*

data class TranslateRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var inputJson: String? = null,

    var language: String? = null,

    var model: String? = null,

    @Secret
    var apiKey: String? = null
)
