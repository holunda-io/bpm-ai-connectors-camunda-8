package io.holunda.connector.executor

import com.fasterxml.jackson.databind.annotation.*
import io.camunda.connector.api.annotation.*
import io.holunda.connector.common.json.*
import io.holunda.connector.common.openai.*
import io.holunda.connector.planner.*

data class ExecutorRequest(
  @field:JsonDeserialize(using = RawJsonDeserializer::class)
  val inputJson: String,
  val task: Task,
  val model: Model,

  @Secret
  var apiKey: String
)
