package io.holunda.connector.common.openai

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*

class LangchainClient {

  companion object {
    const val BASE_URL = "http://localhost:9999"
  }

  private val client = HttpClient {
    install(ContentNegotiation) {
      json(Json {
        prettyPrint = true
      })
      expectSuccess = true
    }
    install(HttpTimeout) {
      requestTimeoutMillis = HttpTimeout.INFINITE_TIMEOUT_MS
      connectTimeoutMillis = HttpTimeout.INFINITE_TIMEOUT_MS
      socketTimeoutMillis = HttpTimeout.INFINITE_TIMEOUT_MS
    }
  }

  fun run(type: String, payload: String): String = runBlocking {
    client.post("$BASE_URL/$type") {
      contentType(ContentType.Application.Json)
      setBody(payload)
    }.body()
  }

}
