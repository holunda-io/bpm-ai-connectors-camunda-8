package io.holunda.connector.openapi

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-openapi",
    inputVariables = [
        "inputJson",
        "taskDescription",
        "specUrl",
        "outputSchema",
        "advanced",
        "model"
    ],
    type = "io.holunda:connector-openapi:1"
)
class OpenApiAgentFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing OpenApiAgentFunction")
        val connectorRequest = context.bindVariables(OpenApiAgentRequest::class.java)
        logger.info("OpenApiAgentFunction request: $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: OpenApiAgentRequest): OpenApiAgentResult {
        val result = LLMServiceClient.run("openapi", OpenApiAgentTask.fromRequest(request))
        logger.info("OpenApiAgentFunction result: $result")
        return OpenApiAgentResult(result)
    }

    companion object : KLogging()
}
