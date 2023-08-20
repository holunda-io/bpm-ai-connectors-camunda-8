package io.holunda.connector.extract

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.error.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import mu.*

@OutboundConnector(
    name = "gpt-extract",
    inputVariables = [
        "inputJson",
        "instructions",
        "extractionJson",
        "mode",
        "entitiesDescription",
        "model"
    ],
    type = "io.holunda:connector-extract:1"
)
class ExtractFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing ExtractFunction")
        val connectorRequest = context.variables.readFromJson<ExtractRequest>()
        logger.info("ExtractFunction request: $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: ExtractRequest): ExtractResult {
        val result = LLMServiceClient.run("extract", ExtractTask.fromRequest(request))
        logger.info("ExtractFunction result: $result")
        return ExtractResult(result)
    }

    companion object : KLogging()
}
