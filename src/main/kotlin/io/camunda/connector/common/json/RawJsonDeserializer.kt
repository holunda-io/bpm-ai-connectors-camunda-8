package io.camunda.connector.common.json

import com.fasterxml.jackson.core.*
import com.fasterxml.jackson.databind.*

class RawJsonDeserializer : JsonDeserializer<String?>() {
    override fun deserialize(parser: JsonParser, ctx: DeserializationContext?): String {
        val mapper = parser.codec as ObjectMapper
        val node: JsonNode = mapper.readTree(parser)
        return mapper.writeValueAsString(node)
    }
}