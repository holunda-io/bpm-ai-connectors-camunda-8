package io.camunda.connector

import io.camunda.connector.api.annotation.OutboundConnector
import io.camunda.connector.api.error.ConnectorException
import io.camunda.connector.api.outbound.OutboundConnectorContext
import io.camunda.connector.api.outbound.OutboundConnectorFunction
import org.slf4j.LoggerFactory
import java.util.*

@OutboundConnector(name = "c8-gpt-extractdata", inputVariables = ["message", "businessKey"], type = "c8-gpt-extractdata")
class GPTExtractDataFunction : OutboundConnectorFunction {
    @Throws(Exception::class)
    override fun execute(context: OutboundConnectorContext): Any {
        LOGGER.info("Executing my connector with request")
        val connectorRequest = context.getVariablesAsType(MyConnectorRequest::class.java)
        context.validate(connectorRequest)
        context.replaceSecrets(connectorRequest)
        return executeConnector(connectorRequest)
    }

    private fun executeConnector(connectorRequest: MyConnectorRequest): MyConnectorResult {
        // TODO: implement connector logic
        LOGGER.info("Executing my connector with request {}", connectorRequest)
        val message = connectorRequest.message
        if (message != null && message.lowercase(Locale.getDefault()).startsWith("fail")) {
            throw ConnectorException("FAIL", "My property started with 'fail', was: $message")
        }
        val result = MyConnectorResult()
        result.myProperty = "Message received: " + message + connectorRequest.businessKey
        return result
    }

    companion object {
        private val LOGGER = LoggerFactory.getLogger(GPTExtractDataFunction::class.java)
    }
}
