package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.database.*
import io.holunda.connector.openapi.*
import mu.*
import org.slf4j.*
import java.util.*


@OutboundConnector(
  name = "gpt-retrieval",
  inputVariables = ["query", "databaseUrl", "embeddingProvider", "embeddingModel", "model", "apiKey"],
  type = "gpt-retrieval"
)
class RetrievalFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing RetrievalFunction")
    val connectorRequest = context.variables.readFromJson<RetrievalRequest>()
    logger.info("Request: {}", connectorRequest)
    context.validate(connectorRequest)
    context.replaceSecrets(connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: RetrievalRequest): RetrievalResult {
    val result = LangchainClient.run("retrieval",
      RetrievalTask(
        request.model.modelId,
        request.query,
        request.databaseUrl,
        request.embeddingProvider,
        request.embeddingModel
      )
    )

    logger.info("RetrievalFunction result: $result")

    return RetrievalResult(result)
  }

  data class RetrievalTask(
    val model: String,
    val query: String,
    val database_url: String,
    val embedding_provider: String,
    val embedding_model: String,
  )

  companion object : KLogging()
}
