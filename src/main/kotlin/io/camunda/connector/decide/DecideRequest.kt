package io.camunda.connector.decide

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.common.json.*

data class DecideRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    var inputJson: String? = null,

    var instructions: String? = null,

    var outputType: DecisionOutputType? = null,

    var possibleValues: List<Any>? = null,

    var model: String? = null,

    @Secret
    var apiKey: String? = null
)

enum class DecisionOutputType(name: String) {
    BOOLEAN("Boolean"),
    NUMERIC("Numeric"),
    STRING("String")
}