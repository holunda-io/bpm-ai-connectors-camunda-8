package io.holunda.connector.process

import com.fasterxml.jackson.module.kotlin.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-process",
    inputVariables = [
        "inputJson",
        "taskDescription",
        "activities",
        "model"
    ],
    type = "io.holunda:connector-process:1"
)
class ProcessAgentFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing ProcessAgentFunction")
        val connectorRequest = context.bindVariables(ProcessAgentRequest::class.java)
        logger.info("ProcessAgentFunction request: $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: ProcessAgentRequest): ProcessAgentResult {
        val result = LLMServiceClient.run("process", ProcessAgentTask.fromRequest(request))

        val elements = jacksonObjectMapper().treeToValue<List<Element>>(result.get("elements"))
        val flows = jacksonObjectMapper().treeToValue<List<Flow>>(result.get("flows"))

        val creator = ProcessModelCreator(request.activities)
        val processId = creator.createProcess(elements, flows)

        logger.info("ProcessAgentFunction result: $processId")

        return ProcessAgentResult(processId ?: "")
    }

    companion object : KLogging()
}
