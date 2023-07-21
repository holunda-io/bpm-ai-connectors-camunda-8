package io.holunda.connector

import com.fasterxml.jackson.core.type.*
import com.fasterxml.jackson.databind.*
import io.camunda.zeebe.model.bpmn.*
import io.camunda.zeebe.model.bpmn.builder.*
import java.io.*
import java.util.*

class ProcessModelCreator {

  private val nodeBuilders = mutableMapOf<String, AbstractFlowNodeBuilder<*, *>>()
  private val adjacencyList = mutableMapOf<String, MutableList<Map<String, String>>>()

  companion object {
    val templates = mapOf(
      "customer_database" to "io.holunda.connector.database.v1"
    )
    val icons = mapOf(
      "customer_database" to "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48IS0tIFVwbG9hZGVkIHRvOiBTVkcgUmVwbywgd3d3LnN2Z3JlcG8uY29tLCBHZW5lcmF0b3I6IFNWRyBSZXBvIE1peGVyIFRvb2xzIC0tPg0KPHN2ZyB3aWR0aD0iODAwcHgiIGhlaWdodD0iODAwcHgiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCjxwYXRoIGQ9Ik0zLjE3MDA0IDcuNDM5OTRMMTIgMTIuNTQ5OUwyMC43NyA3LjQ2OTkxIiBzdHJva2U9IiMyOTJEMzIiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4NCjxwYXRoIGQ9Ik0xMiAyMS42MDk5VjEyLjUzOTkiIHN0cm9rZT0iIzI5MkQzMiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPg0KPHBhdGggZD0iTTIxLjYxIDEyLjgzVjkuMTdDMjEuNjEgNy43OSAyMC42MiA2LjExMDAyIDE5LjQxIDUuNDQwMDJMMTQuMDcgMi40OEMxMi45MyAxLjg0IDExLjA3IDEuODQgOS45Mjk5OSAyLjQ4TDQuNTkgNS40NDAwMkMzLjM4IDYuMTEwMDIgMi4zOTAwMSA3Ljc5IDIuMzkwMDEgOS4xN1YxNC44M0MyLjM5MDAxIDE2LjIxIDMuMzggMTcuODkgNC41OSAxOC41Nkw5LjkyOTk5IDIxLjUyQzEwLjUgMjEuODQgMTEuMjUgMjIgMTIgMjJDMTIuNzUgMjIgMTMuNSAyMS44NCAxNC4wNyAyMS41MiIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8cGF0aCBkPSJNMTkuMiAyMS40QzIwLjk2NzMgMjEuNCAyMi40IDE5Ljk2NzMgMjIuNCAxOC4yQzIyLjQgMTYuNDMyNyAyMC45NjczIDE1IDE5LjIgMTVDMTcuNDMyNyAxNSAxNiAxNi40MzI3IDE2IDE4LjJDMTYgMTkuOTY3MyAxNy40MzI3IDIxLjQgMTkuMiAyMS40WiIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8cGF0aCBkPSJNMjMgMjJMMjIgMjEiIHN0cm9rZT0iIzI5MkQzMiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPg0KPC9zdmc+"
    )
  }

  fun createProcess(
    elementDefinitions: List<Map<String, Any>>,
    flowDefinitions: List<Map<String, String>>,
    connectorDefinitions: Map<String, Any>
  ): BpmnModelInstance? {
    // Create adjacency list for depth-first creation of process
    for (flowDefinition in flowDefinitions) {
      val from = flowDefinition["from"]!!
      adjacencyList.getOrPut(from) { mutableListOf() }.add(flowDefinition)
    }

    val nodeStack = Stack<String>()

    val processBuilder = Bpmn.createExecutableProcess()
    registerNamespaces(processBuilder)

    nodeStack.push(
      createStartEvent(elementDefinitions, processBuilder)
    )

    // Create process depth-first
    while (!nodeStack.isEmpty()) {
      val fromNodeName = nodeStack.pop()

      adjacencyList[fromNodeName]?.forEach { outgoingFlowDefinition ->
        val toNodeName = outgoingFlowDefinition["to"]!!
        val fromNode = nodeBuilders[fromNodeName]!!
        val condition = outgoingFlowDefinition["condition"]

        if (!condition.isNullOrEmpty()) {
          fromNode.condition(condition)
        }

        // Create the 'to' node if it has not been created yet
        if (!nodeBuilders.containsKey(toNodeName)) {
          // flow is automatically added by builder method
          createNode(elementDefinitions, toNodeName, fromNodeName)
        } else {
          // If node already exists, we need to manually add the flow to it
          val toNode = nodeBuilders[toNodeName]!!
          fromNode.connectTo(toNode.element.id)
        }

        nodeStack.push(toNodeName)
      }
    }
    //return Bpmn.convertToString(processBuilder.done())
    return processBuilder.done()
  }

  private fun createNode(elementDefinitions: List<Map<String, Any>>, toNodeName: String, nodeName: String) {
    val toNodeDefinition = elementDefinitions
      .firstOrNull { it["name"] == toNodeName }
      ?: throw IllegalStateException("Flow target $toNodeName not found.")

    val type = toNodeDefinition["type"] as String
    val name = toNodeDefinition["name"] as String
    var builder = nodeBuilders[nodeName]!!

    builder = when (type) {
      "end" -> builder.endEvent(name)
      "gateway" -> builder.exclusiveGateway(name)
      else -> createConnectorTask(builder, toNodeDefinition)
    }
    nodeBuilders[name] = builder
  }

  private fun createStartEvent(elementDefinitions: List<Map<String, Any>>, processBuilder: ProcessBuilder) =
    elementDefinitions
      .firstOrNull { it["type"] == "start" }
      ?.let { startDefinition ->
        val name = startDefinition["name"] as String
        val startEventBuilder = processBuilder.startEvent(name)
        nodeBuilders[name] = startEventBuilder
        name
      } ?: throw IllegalArgumentException("No start event found")


  private fun createConnectorTask(builder: AbstractFlowNodeBuilder<*, *>, elementDefinition: Map<String, Any>): AbstractFlowNodeBuilder<*, *> {
    val type = elementDefinition["type"]
    return if (type == "user_task") {
      builder.userTask(elementDefinition["name"] as String)
    } else {
      addAttributesForConnector(builder, elementDefinition)
    }
  }

  private fun addAttributesForConnector(builder: AbstractFlowNodeBuilder<*, *>, elementDefinition: Map<String, Any>): ServiceTaskBuilder {
    val serviceTaskBuilder = builder.serviceTask(elementDefinition["name"] as String)
    when (elementDefinition["type"] as String) {
      "customer_database" -> {
        addDatabaseConnectorAttributes(serviceTaskBuilder, elementDefinition)
      }
    }
    addDefaultInputs(serviceTaskBuilder, elementDefinition)
    addConnectorTemplate(serviceTaskBuilder, elementDefinition)
    return serviceTaskBuilder
  }

  private fun addDatabaseConnectorAttributes(serviceTaskBuilder: ServiceTaskBuilder, elementDefinition: Map<String, Any>) {
    serviceTaskBuilder
      .zeebeJobType("gpt-database")
      .zeebeInput("http://localhost:8000", "databaseUrl")
      .zeebeInput(elementDefinition["instruction"] as String, "taskDescription")
      .zeebeInput(elementDefinition["output_schema"].toString(), "outputSchema")
      .zeebeInput("NULL", "missingDataBehavior")
      .zeebeInput(elementDefinition["input_variables"].toString(), "inputJson")
  }

  private fun addDefaultInputs(serviceTaskBuilder: ServiceTaskBuilder, elementDefinition: Map<String, Any>) {
    serviceTaskBuilder
      .zeebeInput("secrets.OPENAI_API_KEY", "apiKey")
      .zeebeInput("GPT_4", "model")
      .zeebeTaskHeader("resultExpression", "={" + elementDefinition["output_variable"] + ": result}")
  }

  private fun registerNamespaces(processBuilder: ProcessBuilder) {
    val root = processBuilder.element.modelInstance.document.rootElement
    root.registerNamespace("zeebe", "http://camunda.org/schema/zeebe/1.0")
    root.registerNamespace("modeler", "http://camunda.org/schema/modeler/1.0")
  }

  private fun addConnectorTemplate(builder: AbstractFlowNodeBuilder<*, *>, elementDefinition: Map<String, Any>) {
    val dom = builder.element.domElement
    dom.setAttribute("http://camunda.org/schema/zeebe/1.0", "modelerTemplate", templates[elementDefinition["type"]]!!)
    dom.setAttribute("http://camunda.org/schema/zeebe/1.0", "modelerTemplateVersion", "1")
    dom.setAttribute(
      "http://camunda.org/schema/zeebe/1.0",
      "modelerTemplateIcon",
      icons[elementDefinition["type"]]!!
    )
  }

  fun parseJsonFile(filePath: String): List<Map<String, Any>> {
    val objectMapper = ObjectMapper()
    return try {
      objectMapper.readValue(
        File(this.javaClass.getResource(filePath)!!.file),
        object : TypeReference<List<Map<String, Any>>>() {})
    } catch (e: IOException) {
      throw RuntimeException("Failed to parse JSON file: $filePath", e)
    }
  }

  fun parseJsonFileString(filePath: String): List<Map<String, String>> {
    val objectMapper = ObjectMapper()
    return try {
      objectMapper.readValue(
        File(this.javaClass.getResource(filePath)!!.file),
        object : TypeReference<List<Map<String, String>>>() {})
    } catch (e: IOException) {
      throw RuntimeException("Failed to parse JSON file: $filePath", e)
    }
  }

  fun writeModelToFile(modelInstance: BpmnModelInstance?, filePath: String) {
    try {
      val file = File(filePath)
      Bpmn.writeModelToFile(file, modelInstance)
    } catch (e: Exception) {
      throw RuntimeException("Failed to write BPMN model to file: $filePath", e)
    }
  }
}

