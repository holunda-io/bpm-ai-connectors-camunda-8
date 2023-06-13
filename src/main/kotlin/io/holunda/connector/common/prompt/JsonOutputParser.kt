package io.holunda.connector.common.prompt

import io.holunda.connector.common.json.*

class JsonOutputParser(
    private val jsonSchema: Map<String, String> = emptyMap()
): OutputParser<Map<String, Any?>> {

    override fun getFormatInstructions() = FORMAT_INSTRUCTION.format(jsonSchema.toJson())

    @Throws
    override fun parse(completion: String): Map<String, Any?> {
        val jsonString = RESPONSE_REGEX.find(completion)?.value ?: throw IllegalArgumentException("No Json found")
        val json = jsonString.toMap()
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

        val RESPONSE_REGEX = "\\{[^}]*}".toRegex()
    }
}
