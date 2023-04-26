package io.holunda.connector.translate

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*

data class TranslateRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val inputJson: String,
    val language: String,
    val model: String,

    @Secret
    var apiKey: String
)
