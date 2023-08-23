package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class OpenApiAgentRequest(
    val inputJson: JsonNode,
    val query: String,
    val specUrl: String,
    val skillStoreUrl: String?,
    val outputSchema: JsonNode?,
    val model: Model
)
