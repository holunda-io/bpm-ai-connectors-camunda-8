package io.holunda.connector.database

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class DatabaseAgentRequest(
    val inputJson: JsonNode,
    val query: QueryConfig,
    val databaseUrl: String,
    val advanced: AdvancedConfig,
    val model: Model
)

data class QueryConfig(
    val query: String,
    val outputType: String,
    val outputSchema: JsonNode?,
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
