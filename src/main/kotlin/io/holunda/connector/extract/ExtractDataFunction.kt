package io.holunda.connector.extract

import com.aallam.openai.api.*
import com.google.gson.reflect.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import org.slf4j.*
import java.util.*

@OptIn(BetaOpenAI::class)
@OutboundConnector(
    name = "gpt-extract",
    inputVariables = ["inputJson", "extractionJson", "missingDataBehavior", "model", "apiKey"],
    type = "gpt-extract"
)
class ExtractDataFunction : OutboundConnectorFunction {

    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOG.info("Executing ExtractDataFunction")
        val connectorRequest = context.getVariablesAsType(ExtractDataRequest::class.java)
        LOG.info("Request: {}", connectorRequest)
        context.validate(connectorRequest)
        context.replaceSecrets(connectorRequest)
        return executeConnector(connectorRequest)
    }

    private fun executeConnector(request: ExtractDataRequest): Map<String, Any?> {
        val openAIClient = OpenAIClient(request.apiKey ?: throw RuntimeException("No OpenAI apiKey set"))

        val jsonOutputParser = JsonOutputParser(
            jsonSchema = request.extractionJson?.jsonToStringMap() ?: emptyMap()
        )

        val prompt = ExtractDataPrompt(
            request.inputJson!!,
            jsonOutputParser.getFormatInstructions()
        )

        val fixingParser = OutputFixingParser(prompt, jsonOutputParser, openAIClient)

        LOG.info("ExtractDataFunction prompt: ${prompt.buildPrompt()}")

        val completedChatHistory = openAIClient.chatCompletion(prompt.buildPrompt())
        var result = fixingParser.parse(completedChatHistory.completionContent())
            .mapValues { if (it.value is String? && (it.value as String?)?.lowercase() == "null") null else it.value }

        result = when (request.missingDataBehavior) {
            MissingDataBehavior.EMPTY -> {
                result.mapValues { it.value ?: "" }
            }
            MissingDataBehavior.ERROR -> {
                if (result.values.any { it == null }) {
                    throw ConnectorException("NULL", "One or more result values are null")
                } else result
            }
            else -> result
        }

        LOG.info("ExtractDataFunction result: $result")

        return result
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(ExtractDataFunction::class.java)
    }
}
