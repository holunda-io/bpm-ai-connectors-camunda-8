package io.holunda.connector.planner

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*

data class PlannerRequest(
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val inputJson: String,
  val taskDescription: String,
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val tools: String,
  val model: Model,

  @Secret
  var apiKey: String
)
