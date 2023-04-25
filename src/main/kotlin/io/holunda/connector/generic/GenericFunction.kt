package io.holunda.connector.generic

import com.aallam.openai.api.*
import com.google.gson.reflect.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import org.slf4j.*
import java.util.*

@OptIn(BetaOpenAI::class)
@OutboundConnector(
    name = "gpt-generic",
    inputVariables = ["inputJson", "taskDescription", "outputFormat", "model", "apiKey"],
    type = "gpt-generic"
)
class GenericFunction : OutboundConnectorFunction {

    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOG.info("Executing GenericFunction")
        val connectorRequest = context.getVariablesAsType(GenericRequest::class.java)
        LOG.info("Request: {}", connectorRequest)
        context.validate(connectorRequest)
        context.replaceSecrets(connectorRequest)
        return executeConnector(connectorRequest)
    }

    private fun executeConnector(request: GenericRequest): Map<String, Any?> {
        val openAIClient = OpenAIClient(request.apiKey ?: throw RuntimeException("No OpenAI apiKey set"))

        val jsonOutputParser = JsonOutputParser(
            jsonSchema = request.outputFormat?.jsonToStringMap() ?: emptyMap()
        )

        val prompt = GenericTaskPrompt(
            request.taskDescription!!,
            request.inputJson!!,
            jsonOutputParser.getFormatInstructions()
        )

        val fixingParser = OutputFixingParser(prompt, jsonOutputParser, openAIClient)

        LOG.info("GenericFunction prompt: ${prompt.buildPrompt()}")

        val completedChatHistory = openAIClient.chatCompletion(prompt.buildPrompt())
        val result = fixingParser.parse(completedChatHistory.completionContent())

        LOG.info("GenericFunction result: $result")

        return result
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(GenericFunction::class.java)
    }
}
