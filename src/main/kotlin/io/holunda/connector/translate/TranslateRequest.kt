package io.holunda.connector.translate

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class TranslateRequest(
  val inputJson: JsonNode,
  val language: String,
  val model: Model,

  @Secret
    var apiKey: String
)
