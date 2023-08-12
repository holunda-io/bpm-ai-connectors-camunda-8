package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.holunda.connector.compose.*
import io.holunda.connector.database.*
import io.holunda.connector.openapi.*
import mu.*
import org.apache.commons.text.*
import org.slf4j.*
import java.util.*


@OutboundConnector(
  name = "gpt-retrieval",
  inputVariables = ["query", "databaseUrl", "embeddingProvider", "embeddingModel", "mode", "model"],
  type = "gpt-retrieval"
)
class RetrievalFunction : OutboundConnectorFunction {

  @Throws(Exception::class)
  override fun execute(context: OutboundConnectorContext): Any {
    logger.info("Executing RetrievalFunction")
    val connectorRequest = context.variables.readFromJson<RetrievalRequest>()
    //val connectorRequest = context.bindVariables(RetrievalRequest::class.java)
    logger.info("Request: {}", connectorRequest)
    return executeConnector(connectorRequest)
  }

  private fun executeConnector(request: RetrievalRequest): RetrievalResult {
    val result = LLMServiceClient.run("retrieval",
      RetrievalTask(
        request.model.modelId,
        request.query,
        request.databaseUrl,
        request.embeddingProvider,
        request.embeddingModel,
        request.mode
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
    val mode: String,
  )

  companion object : KLogging()
}
