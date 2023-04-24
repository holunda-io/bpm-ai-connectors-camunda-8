package io.camunda.connector.common.json

import com.google.gson.*
import com.google.gson.reflect.*

fun String.jsonToMap(): Map<String, String> {
    val type = object : TypeToken<Map<String, String>>() {}.type
    return Gson().fromJson(this, type)
}
