package io.holunda.connector.compose

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*

data class ComposeRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val inputJson: String,
    val description: String,
    val style: String,
    val tone: String,
    val language: String,
    val sender: String,
    val model: String,

    @Secret
    var apiKey: String
)
