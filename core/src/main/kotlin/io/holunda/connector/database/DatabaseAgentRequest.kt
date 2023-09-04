package io.holunda.connector.database

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class DatabaseAgentRequest(
    val inputJson: JsonNode,
    val query: String,
    val databaseUrl: String,
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
