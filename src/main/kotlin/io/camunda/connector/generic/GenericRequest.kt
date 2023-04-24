package io.camunda.connector.generic

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.common.json.*

data class GenericRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var inputJson: String? = null,

    var taskDescription: String? = null,

    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var outputFormat: String? = null,

    var model: String? = null,

    @Secret
    var apiKey: String? = null
)
