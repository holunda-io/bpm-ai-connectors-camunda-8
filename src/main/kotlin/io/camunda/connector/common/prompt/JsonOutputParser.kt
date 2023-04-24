package io.camunda.connector.common.prompt

import com.google.gson.*
import io.camunda.connector.common.json.*

class JsonOutputParser(
    private val jsonSchema: Map<String, String> = emptyMap()
): OutputParser<Map<String, String?>> {

    private val gson = Gson().newBuilder().setPrettyPrinting().create()

    override fun getFormatInstructions() = FORMAT_INSTRUCTION.format(gson.toJson(jsonSchema))

    @Throws
    override fun parse(completion: String): Map<String, String?> {
        val jsonString = RESPONSE_REGEX.find(completion)?.value ?: throw IllegalArgumentException("No Json found")
        val json = jsonString.jsonToMap()
        if (!jsonSchema.keys.all { json.containsKey(it) }) {
            throw IllegalArgumentException("Json is missing one or more required fields")
        }
        return json
    }

    companion object {
        private val FORMAT_INSTRUCTION = """
            You will always output a JSON of the following form:
            %s
            
            You will NEVER output anything other than this JSON.
        """.trimIndent()

        private val RESPONSE_REGEX = "\\{[^}]*}".toRegex()
    }
}