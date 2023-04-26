package io.holunda.connector.generic

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
    name = "gpt-generic",
    inputVariables = ["inputJson", "taskDescription", "outputFormat", "model", "apiKey"],
    type = "gpt-generic"
)
class GenericFunction : OutboundConnectorFunction {

    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOG.info("Executing GenericFunction")
        val connectorRequest = context.variables.readFromJson<GenericRequest>()
        LOG.info("Request: {}", connectorRequest)
        context.validate(connectorRequest)
        context.replaceSecrets(connectorRequest)
        return executeConnector(connectorRequest)
    }

    private fun executeConnector(request: GenericRequest): GenericResult {
        val openAIClient = OpenAIClient(request.apiKey)

        val jsonOutputParser = JsonOutputParser(
            jsonSchema = request.outputFormat.toStringMap()
        )

        val prompt = GenericPrompt(
            request.taskDescription,
            request.inputJson,
            jsonOutputParser.getFormatInstructions()
        )

        val fixingParser = OutputFixingParser(prompt, jsonOutputParser, openAIClient)

        LOG.info("GenericFunction prompt: ${prompt.buildPrompt()}")

        val completedChatHistory = openAIClient.chatCompletion(prompt.buildPrompt(), model = request.model)
        val result = fixingParser.parse(completedChatHistory.completionContent())

        LOG.info("GenericFunction result: $result")

        return GenericResult(result)
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(GenericFunction::class.java)
    }
}
