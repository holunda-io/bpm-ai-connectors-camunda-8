package io.camunda.connector.extract

import io.camunda.connector.api.annotation.OutboundConnector
import io.camunda.connector.api.outbound.OutboundConnectorContext
import io.camunda.connector.api.outbound.OutboundConnectorFunction
import org.slf4j.LoggerFactory
import java.util.*

@OutboundConnector(
    name = "c8-gpt-extractdata",
    inputVariables = ["description", "context"],
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
        println("DESCRIPTION: " + connectorRequest.description + ", CONTEXT:" + connectorRequest.context)
        val result = ExtractDataResult("")
        return result
    }

    companion object {
        private val LOG = LoggerFactory.getLogger(ExtractDataFunction::class.java)
    }
}
