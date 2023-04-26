package io.holunda.connector.translate

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*

data class TranslateRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val inputJson: String,
    val language: String,
    val model: Model,

    @Secret
    var apiKey: String
)
