package io.holunda.connector.common

import com.fasterxml.jackson.core.util.*
import com.fasterxml.jackson.databind.*
import com.fasterxml.jackson.module.kotlin.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.jackson.*
import kotlinx.coroutines.*

object LLMServiceClient {

    var llmServiceUrl = System.getenv("LLM_SERVICE_URL") ?: "http://localhost:9999"

    val client = HttpClient {
        install(ContentNegotiation) {
            jackson {
                configure(SerializationFeature.INDENT_OUTPUT, true)
                setDefaultPrettyPrinter(DefaultPrettyPrinter().apply {
                    indentArraysWith(DefaultPrettyPrinter.FixedSpaceIndenter.instance)
                    indentObjectsWith(DefaultIndenter("  ", "\n"))
                })
            }
        }

        expectSuccess = true

        install(HttpTimeout) {
            requestTimeoutMillis = HttpTimeout.INFINITE_TIMEOUT_MS
            connectTimeoutMillis = HttpTimeout.INFINITE_TIMEOUT_MS
            socketTimeoutMillis = HttpTimeout.INFINITE_TIMEOUT_MS
        }
    }

    val jsonMapper = jacksonObjectMapper()

    inline fun <reified T : Any> run(task: String, request: T): JsonNode = runBlocking {
        val response: String = try {
            async {
                client.post("${llmServiceUrl}/$task") {
                    contentType(ContentType.Application.Json)
                    setBody(jsonMapper.writeValueAsString(request))
                }.body() as String
            }.await()
        } catch (e: Exception) {
            throw LLMClientException()
        }

        jsonMapper.readTree(response)
    }

    class LLMClientException: RuntimeException("LLM request failed")

}
