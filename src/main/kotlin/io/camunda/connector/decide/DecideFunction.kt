package io.camunda.connector.decide

import com.aallam.openai.api.*
import com.google.gson.reflect.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.camunda.connector.common.*
import io.camunda.connector.common.json.*
import io.camunda.connector.common.openai.*
import io.camunda.connector.common.prompt.*
import io.camunda.connector.extract.*
import io.camunda.connector.generic.*
import org.slf4j.*
import java.util.*

@OptIn(BetaOpenAI::class)
@OutboundConnector(
    name = "gpt-decide",
    inputVariables = ["inputJson", "instructions", "outputType", "possibleValues", "model", "apiKey"],
    type = "gpt-decide"
)
class DecideFunction : OutboundConnectorFunction {

    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOG.info("Executing DecideFunction")
        val request = context.getVariablesAsType(DecideRequest::class.java)
        LOG.info("Request: {}", request)
        context.validate(request)
        context.replaceSecrets(request)
        return executeConnector(request)
    }

    private fun executeConnector(request: DecideRequest): Map<String, String?> {
        val openAIClient = OpenAIClient(request.apiKey ?: throw RuntimeException("No OpenAI apiKey set"))

        val jsonOutputParser = JsonOutputParser(
            jsonSchema = mapOf(
                "decision" to "the result value of the decision",
                "reasoning" to "the reasoning behind the decision"
            )
        )

        val prompt = DecidePrompt(
            request.inputJson!!,
            request.instructions!!,
            request.outputType!!.name,
            request.possibleValues?.toString(),
            jsonOutputParser.getFormatInstructions()
        )

        val fixingParser = OutputFixingParser(prompt, jsonOutputParser, openAIClient)

        LOG.info("DecideFunction prompt: ${prompt.buildPrompt()}")

        val completedChatHistory = openAIClient.chatCompletion(prompt.buildPrompt())
        val result = fixingParser.parse(completedChatHistory.completionContent())

        LOG.info("DecideFunction result: $result")

        return result
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(DecideFunction::class.java)
    }
}
