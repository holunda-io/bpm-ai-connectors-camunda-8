package io.holunda.connector.planner

import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.retrieval.*
import mu.*

@OutboundConnector(
    name = "gpt-planner",
    inputVariables = [
        "inputJson",
        "taskDescription",
        "tools",
        "model"
    ],
    type = "io.holunda:connector-planner:1"
)
class PlannerFunction : OutboundConnectorFunction {

    override fun execute(context: OutboundConnectorContext): Any {
        logger.info("Executing PlannerFunction")
        val connectorRequest = context.bindVariables(PlannerRequest::class.java)
        logger.info("PlannerFunction request: $connectorRequest")
        return executeRequest(connectorRequest)
    }

    private fun executeRequest(request: PlannerRequest): PlannerResult {
        val result = LLMServiceClient.run("planner", PlannerTask.fromRequest(request))
        val plan = result.toStringList()
        logger.info("PlannerFunction result: $plan")
        return PlannerResult(
            Task(
                task = request.taskDescription,
                tools = request.tools.toStringMap(),
                plan = plan,
            )
        )
    }

    companion object : KLogging()
}
