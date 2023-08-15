package io.holunda.connector.generic

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import mu.*

@OutboundConnector(
    name = "gpt-generic",
    inputVariables = [
        "inputJson",
        "taskDescription",
        "outputFormat",
        "model"
    ],
    type = "io.holunda:connector-generic:1"
)
class GenericFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing GenericFunction")
        val connectorRequest = context.variables.readFromJson<GenericRequest>()
        logger.info("GenericFunction request $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: GenericRequest): GenericResult {
        val result = LLMServiceClient.run("generic", GenericTask.fromRequest(request))
        logger.info("GenericFunction result: $result")
        return GenericResult(result)
    }

    companion object : KLogging()
}
