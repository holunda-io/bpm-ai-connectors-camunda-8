package io.holunda.connector.common

import com.fasterxml.jackson.core.type.*
import com.fasterxml.jackson.databind.*
import com.fasterxml.jackson.module.kotlin.*

private val mapper = jacksonObjectMapper()

fun JsonNode.toMap(): Map<String, Any?> {
    val typeRef = object : TypeReference<Map<String, Any?>>() {}
    return mapper.convertValue(this, typeRef)
}

fun JsonNode.toStringMap(): Map<String, String> {
    val typeRef = object : TypeReference<Map<String, String>>() {}
    return mapper.convertValue(this, typeRef)
}

fun JsonNode.toStringList(): List<String> {
    val typeRef = object : TypeReference<List<String>>() {}
    return mapper.convertValue(this, typeRef)
}

inline fun <reified T> String.readFromJson() = jacksonObjectMapper().readValue<T>(this)
