package io.holunda.connector.decide

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-decide",
    inputVariables = [
        "inputJson",
        "instructions",
        "outputType",
        "possibleValues",
        "model"
    ],
    type = "io.holunda:connector-decide:1"
)
class DecideFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing DecideFunction")
        val connectorRequest = context.bindVariables(DecideRequest::class.java)
        logger.info("DecideFunction request: $connectorRequest")
        return executeRequest(DecideTask.fromRequest(connectorRequest))
    }

    private fun executeRequest(decideTask: DecideTask): DecideResult {
        val result = LLMServiceClient.run("decide", decideTask)
        logger.info("DecideFunction result: $result")
        return DecideResult(result)
    }

    companion object : KLogging()
}
