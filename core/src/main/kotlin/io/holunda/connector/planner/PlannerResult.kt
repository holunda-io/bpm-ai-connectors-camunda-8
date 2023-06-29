package io.holunda.connector.planner

data class PlannerResult(
  val result: Any
)

data class Task(
  val task: String,
  val tools: Map<String, String>,
  val plan: List<String>,
  val currentStep: Map<String, String>? = null,
  val pastSteps: List<String> = emptyList(),
  val results: List<String> = emptyList(),
)
