package io.holunda.connector.executor

import com.fasterxml.jackson.databind.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.*
import io.holunda.connector.planner.*

data class ExecutorRequest(
  val inputJson: JsonNode,
  val task: Task,
  val model: Model,

  @Secret
  var apiKey: String
)
