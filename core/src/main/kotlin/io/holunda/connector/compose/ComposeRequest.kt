package io.holunda.connector.compose

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class ComposeRequest(
  val inputJson: JsonNode,
  val description: String,
  val style: String,
  val type: String,
  val tone: String,
  val length: String,
  val language: String,
  val sender: String?,
  val template: String?,
  val constitutionalPrinciple: String?,
  val customPrinciple: String?,
  val model: Model,

  @Secret
    var apiKey: String
)
