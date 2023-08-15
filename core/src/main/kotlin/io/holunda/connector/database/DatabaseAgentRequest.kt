package io.holunda.connector.database

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class DatabaseAgentRequest(
    val inputJson: JsonNode,
    val query: String,
    val databaseUrl: String,
    val skillStoreUrl: String?,
    val outputSchema: JsonNode,
    val model: Model
)
