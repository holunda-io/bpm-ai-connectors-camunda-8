package io.holunda.connector

import com.fasterxml.jackson.module.kotlin.*
import io.camunda.connector.runtime.core.*
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.ktor.serialization.jackson.*
import io.ktor.server.application.*

import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun main() {
    embeddedServer(Netty, port = 9999) { module() }.start(wait = true)
}

fun Application.module() {
    install(ContentNegotiation) {
        jackson {}
    }

    routing {
        post("/createOutputVariables") {
            val request = call.receive<CreateOutputVariablesRequest>()
            val result = ConnectorRuntime.createOutputVariables(request.context, request.resultExpression)
            call.respond(result)
        }

        post("/examineErrorExpression") {
            val request = call.receive<ExamineErrorExpressionRequest>()
            val result = ConnectorRuntime.examineErrorExpression(request.context, request.errorExpression)
            call.respondNullable(result)
        }
    }
}

data class CreateOutputVariablesRequest(val context: Any, val resultExpression: String)
data class ExamineErrorExpressionRequest(val context: Any, val errorExpression: String)


object ConnectorRuntime {

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
