package io.camunda.connector.common.prompt

import com.google.gson.*
import com.google.gson.reflect.*
import kotlin.jvm.Throws

class JsonOutputParser: OutputParser<Map<String, String>> {

    private val fields: MutableList<JsonField> = mutableListOf()

    fun requireField(name: String, description: String) {
        fields.add(JsonField(name, description))
    }

    override fun getFormatInstructions() = FORMAT_INSTRUCTION.format(getFieldDescriptions())

    @Throws
    override fun parse(completion: String): Map<String, String> {
        val jsonString = RESPONSE_REGEX.find(completion)?.value
            ?: throw IllegalArgumentException("No Json found")
        val json = jsonToMap(jsonString)
        if (!fields.all { json.containsKey(it.name) }) {
            throw IllegalArgumentException("Json is missing one or more required fields")
        }
        return json
    }

    private fun jsonToMap(jsonString: String): Map<String, String> {
        val type = object : TypeToken<Map<String, String>>() {}.type
        return gson.fromJson(jsonString, type)
    }

    private fun getFieldDescriptions(): String = fields.joinToString("\n") {
        "- ${it.name}: ${it.description}"
    }

    private val gson = Gson()

    companion object {
        private val FORMAT_INSTRUCTION = """
            You will always output a JSON with the following fields:
            %s
            
            You will NEVER output anything other than this JSON.
        """.trimIndent()

        private val RESPONSE_REGEX = "\\{[^}]*}".toRegex()
    }

    data class JsonField(val name: String, val description: String)
}