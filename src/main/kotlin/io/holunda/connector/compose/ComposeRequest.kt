package io.holunda.connector.compose

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class ComposeRequest(
  val inputJson: JsonNode,
  val description: String,
  val style: String,
  val tone: String,
  val language: String,
  val sender: String,
  val model: Model,

  @Secret
    var apiKey: String
)
