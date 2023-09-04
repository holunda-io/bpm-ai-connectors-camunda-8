package io.holunda.connector.translate

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-translate",
    inputVariables = [
        "inputJson",
        "language",
        "model"
    ],
    type = "io.holunda.connector.translate:1"
)
class TranslateFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing TranslateFunction")
        val connectorRequest = context.bindVariables(TranslateRequest::class.java)
        logger.info("TranslateFunction request: $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: TranslateRequest): TranslateResult {
        val result = LLMServiceClient.run("translate", TranslateTask.fromRequest(request))
        logger.info("TranslateFunction result: $result")
        return TranslateResult(result)
    }

    companion object : KLogging()
}
