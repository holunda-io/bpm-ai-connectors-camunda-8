package io.holunda.connector.executor

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*
import io.holunda.connector.planner.*

data class ExecutorRequest(
    val inputJson: JsonNode,
    val taskObject: Task,
    val result: String?,
    val model: Model
)
