package io.holunda.feel.core

import io.camunda.connector.runtime.core.*

object FeelEngineWrapper {

    fun createOutputVariables(context: Any, resultExpression: String): Map<String, Any> {
        return ConnectorHelper.createOutputVariables(
            context,
            null,
            resultExpression
        )
    }

    fun examineErrorExpression(context: Any, errorExpression: String): Any? {
        return ConnectorHelper.examineErrorExpression(
            context,
            mapOf("errorExpression" to errorExpression)
        ).map { it }.orElse(null)
    }
}
