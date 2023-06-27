package io.holunda.connector.planner

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*

data class PlannerRequest(
  val inputJson: JsonNode,
  val taskDescription: String,
  val tools: JsonNode,
  val model: Model,

  @Secret
  var apiKey: String
)
