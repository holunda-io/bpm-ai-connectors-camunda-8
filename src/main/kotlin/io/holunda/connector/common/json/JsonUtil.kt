package io.holunda.connector.common.json

import com.google.gson.*
import com.google.gson.reflect.*

fun String.jsonToMap(): Map<String, Any?> {
    val type = object : TypeToken<Map<String, Any?>>() {}.type
    return Gson().fromJson(this, type)
}

fun String.jsonToStringMap(): Map<String, String> {
    val type = object : TypeToken<Map<String, String>>() {}.type
    return Gson().fromJson(this, type)
}

fun Map<String,Any?>.transformStringValue(key: String, f: (String?) -> Any?) =
    this.mapValues { (k, v) -> if (k == key && v is String?) f(v) else v }
