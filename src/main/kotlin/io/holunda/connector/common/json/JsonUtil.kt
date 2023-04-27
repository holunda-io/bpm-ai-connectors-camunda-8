package io.holunda.connector.common.json

import com.fasterxml.jackson.core.type.*
import com.fasterxml.jackson.module.kotlin.*

private val mapper = jacksonObjectMapper()
private val writer = mapper.writerWithDefaultPrettyPrinter()

fun String.toMap(): Map<String, Any?> {
    val typeRef = object : TypeReference<Map<String, Any?>>() {}
    return mapper.readValue(this, typeRef)
}

fun String.toStringMap(): Map<String, String> {
    val typeRef = object : TypeReference<Map<String, String>>() {}
    return mapper.readValue(this, typeRef)
}

fun Map<String,Any?>.transformStringValue(key: String, f: (String?) -> Any?) =
    this.mapValues { (k, v) -> if (k == key && v is String?) f(v) else v }

inline fun <reified T> String.readFromJson() = jacksonObjectMapper().readValue<T>(this)

fun Any.toJson() = writer.writeValueAsString(this)!!
