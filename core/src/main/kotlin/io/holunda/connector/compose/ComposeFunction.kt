package io.holunda.connector.compose

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import mu.*
import org.apache.commons.text.*

@OutboundConnector(
    name = "gpt-compose",
    inputVariables = [
        "inputJson",
        "description",
        "temperature",
        "type",
        "style",
        "tone",
        "length",
        "language",
        "sender",
        "customPrinciple",
        "constitutionalPrinciple",
        "model"
    ],
    type = "io.holunda:connector-compose:1"
)
class ComposeFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing ComposeFunction")
        val unescapedVariables = StringEscapeUtils.unescapeJson(context.variables) // TODO remove when Camunda fixes this in zeebe :P zeebe/issues/9859
        val connectorRequest = unescapedVariables.readFromJson<ComposeRequest>()
        logger.info("ComposeFunction request: $connectorRequest")
        return executeRequest(ComposeTask.fromRequest(connectorRequest))
    }

    private fun executeRequest(composeTask: ComposeTask): ComposeResult {
        val result = LLMServiceClient.run("compose", composeTask)
        logger.info("ComposeFunction result: $result")
        return ComposeResult(result)
    }

    companion object : KLogging()
}
