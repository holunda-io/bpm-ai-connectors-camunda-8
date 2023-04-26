package io.holunda.connector.decide

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*

data class DecideRequest(
    @field:JsonDeserialize(using = RawJsonDeserializer::class)
    val inputJson: String,
    val instructions: String,
    val outputType: DecisionOutputType,
    val possibleValues: List<Any>?,
    val model: Model,

    @Secret
    var apiKey: String
)

enum class DecisionOutputType(name: String) {
    BOOLEAN("Boolean"),
    INTEGER("Integer"),
    STRING("String")
}