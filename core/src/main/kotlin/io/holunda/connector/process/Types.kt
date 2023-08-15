package io.holunda.connector.process

import com.fasterxml.jackson.databind.*

data class ActivityDefinition(
    val task: String?,
    val description: String,
    val attributes: Map<String, String> = mapOf()
)

data class Element(
    val type: String,
    val name: String,
    val instruction: String?,
    val input_variables: List<String> = emptyList(),
    val output_variable: String?,
    val output_schema: JsonNode?
) {
    fun isStartEvent() = (type == "start")
}

fun List<Element>.findStartEvent() = firstOrNull { it.isStartEvent() }
fun List<Element>.findByName(name: String) = firstOrNull { it.name == name }

data class Flow(
    val from: String,
    val to: String,
    val condition: String?,
)
