package io.camunda.connector.extract

import com.aallam.openai.api.*
import com.google.gson.Gson
import io.camunda.connector.api.annotation.OutboundConnector
import io.camunda.connector.api.outbound.OutboundConnectorContext
import io.camunda.connector.api.outbound.OutboundConnectorFunction
import io.camunda.connector.common.openai.*
import io.camunda.connector.common.prompt.*
import org.slf4j.LoggerFactory
import java.util.*

@OptIn(BetaOpenAI::class)
@OutboundConnector(
    name = "c8-gpt-extractdata",
    inputVariables = ["message", "businessKey"],
    type = "c8-gpt-extractdata"
)
class ExtractDataFunction : OutboundConnectorFunction {

    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOG.info("Executing my connector with request")
        val connectorRequest = context.getVariablesAsType(ExtractDataRequest::class.java)
        context.validate(connectorRequest)
        context.replaceSecrets(connectorRequest)
        return executeConnector(connectorRequest)
    }

    private fun executeConnector(connectorRequest: ExtractDataRequest): ExtractDataResult {
        LOG.info("Executing my connector with request {}", connectorRequest)

        val openAIClient = OpenAIClient(connectorRequest.apiKey!!)

        val jsonOutputParser = JsonOutputParser().apply {
            requireField("result",
                "Contains the result of your decision based on the input values and the task description."
            )
            requireField("reasoning",
                "Contains a short and concise description of your reasoning for the \"result\" decision"
            )
        }
        val prompt = GenericTaskPrompt(
            connectorRequest.message!!,
            mapOf("input" to connectorRequest.input!!),
            jsonOutputParser.getFormatInstructions()
        )
        val fixingParser = OutputFixingParser(prompt, jsonOutputParser, openAIClient)

        LOG.info("Prompt: ${prompt.buildPrompt()}")

        val chatHistory = openAIClient.chatCompletion(prompt.buildPrompt())
        val result = fixingParser.parse(chatHistory.latest())

        LOG.info("Worker result: $result")

        return ExtractDataResult(Gson().toJson(result))
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(ExtractDataFunction::class.java)
    }
}
