package io.holunda.connector.translate

import com.aallam.openai.api.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import org.slf4j.*
import java.util.*

@OptIn(BetaOpenAI::class)
@OutboundConnector(
    name = "gpt-translate",
    inputVariables = ["inputJson", "language", "model", "apiKey"],
    type = "gpt-translate"
)
class TranslateFunction : OutboundConnectorFunction {

    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOG.info("Executing TranslateFunction")
        val connectorRequest = context.variables.readFromJson<TranslateRequest>()
        LOG.info("Request: {}", connectorRequest)
        context.validate(connectorRequest)
        context.replaceSecrets(connectorRequest)
        return executeConnector(connectorRequest)
    }

    private fun executeConnector(request: TranslateRequest): TranslateResult {
        val openAIClient = OpenAIClient(request.apiKey)

        val jsonOutputParser = JsonOutputParser(
            jsonSchema = request.inputJson.toStringMap()
                .mapValues { "${it.key} translated into ${request.language}" }
        )

        val prompt = TranslatePrompt(
            request.inputJson,
            request.language,
            jsonOutputParser.getFormatInstructions()
        )

        val fixingParser = OutputFixingParser(prompt, jsonOutputParser, openAIClient)

        LOG.info("TranslateFunction prompt: ${prompt.buildPrompt()}")

        val completedChatHistory = openAIClient.chatCompletion(prompt.buildPrompt())
        val result = fixingParser.parse(completedChatHistory.completionContent())

        LOG.info("TranslateFunction result: $result")

        return TranslateResult(translated = result)
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(TranslateFunction::class.java)
    }
}
