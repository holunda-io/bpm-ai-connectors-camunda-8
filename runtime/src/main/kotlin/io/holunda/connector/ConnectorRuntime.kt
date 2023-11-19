package io.holunda.connector

import com.fasterxml.jackson.module.kotlin.*
import io.camunda.connector.api.error.BpmnError
import io.camunda.connector.runtime.core.*
import py4j.*
import java.util.Optional

fun main() = GatewayServer(ConnectorRuntime()).start()

class ConnectorRuntime {

    fun createOutputVariables(context: String, resultExpression: String): Map<String, Any> {
        return ConnectorHelper.createOutputVariables(
            jacksonObjectMapper().readValue(context),
            null,
            resultExpression
        )
    }

    fun examineErrorExpression(context: String, errorExpression: String): String {
        return ConnectorHelper.examineErrorExpression(
            jacksonObjectMapper().readValue(context),
            mapOf("errorExpression" to errorExpression)
        ).map { it.code }.orElse("None")
    }
}
