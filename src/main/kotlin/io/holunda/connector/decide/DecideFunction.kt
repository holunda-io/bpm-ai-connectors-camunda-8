package io.holunda.connector.decide

import com.aallam.openai.api.*
import com.google.gson.reflect.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.common.prompt.*
import io.holunda.connector.decide.DecisionOutputType.*
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

    private fun executeConnector(request: DecideRequest): Map<String, Any?> {
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
        var result = fixingParser.parse(completedChatHistory.completionContent())

        result = when (request.outputType) {
            BOOLEAN -> result.transformStringValue("decision") { it.toBoolean() }
            INTEGER -> result.transformStringValue("decision") { it?.toIntOrNull() }
            STRING, null -> result
        }

        LOG.info("DecideFunction result: $result")

        return result
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(DecideFunction::class.java)
    }
}
