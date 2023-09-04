package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class OpenApiAgentRequest(
    val inputJson: JsonNode,
    val query: String,
    val specUrl: String,
    val advanced: AdvancedConfig,
    val outputSchema: JsonNode?,
    val model: Model
)

data class AdvancedConfig(
    val skillMode: String,
    val skillDatabase: SkillDatabaseConfig?
)

data class SkillDatabaseConfig(
    val type: String,
    val url: String,
    val password: String?,
)
