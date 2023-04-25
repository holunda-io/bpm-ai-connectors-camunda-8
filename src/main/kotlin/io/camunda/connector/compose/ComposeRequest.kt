package io.camunda.connector.compose

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.common.json.*

data class ComposeRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var inputJson: String? = null,

    var description: String? = null,

    var style: String? = null,

    var tone: String? = null,

    var language: String? = null,

    var sender: String? = null,

    var model: String? = null,

    @Secret
    var apiKey: String? = null
)
