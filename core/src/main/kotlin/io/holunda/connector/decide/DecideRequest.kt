package io.holunda.connector.decide

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class DecideRequest(
    val inputJson: JsonNode,
    val instructions: String,
    val outputType: String,
    val possibleValues: List<Any>?,
    val strategy: String?,
    val model: Model
)
