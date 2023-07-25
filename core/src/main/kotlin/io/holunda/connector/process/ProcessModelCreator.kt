package io.holunda.connector.process

import com.fasterxml.jackson.core.type.*
import com.fasterxml.jackson.databind.*
import com.fasterxml.jackson.module.kotlin.*
import io.camunda.zeebe.client.*
import io.camunda.zeebe.model.bpmn.*
import io.camunda.zeebe.model.bpmn.builder.*
import java.io.*
import java.util.*

private const val ZEEBE_SCHEMA = "http://camunda.org/schema/zeebe/1.0"
private const val MODELER_SCHEMA = "http://camunda.org/schema/modeler/1.0"

class ProcessModelCreator(val activityDefinitions: Map<String, ActivityDefinition>) {

  private val nodeBuilders = mutableMapOf<String, AbstractFlowNodeBuilder<*, *>>()
  private val adjacencyList = mutableMapOf<String, MutableList<Flow>>()

  companion object {
    val objectMapper = jacksonObjectMapper().enable(SerializationFeature.INDENT_OUTPUT)

    val templates = mapOf(
      "gpt-database" to "io.holunda.connector.database.v1",
      "gpt-openapi" to "io.holunda.connector.openapi.v1",
      "gpt-retrieval" to "io.holunda.connector.retrieval.v1",
    )
    val icons = mapOf(
      "gpt-database" to "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48IS0tIFVwbG9hZGVkIHRvOiBTVkcgUmVwbywgd3d3LnN2Z3JlcG8uY29tLCBHZW5lcmF0b3I6IFNWRyBSZXBvIE1peGVyIFRvb2xzIC0tPg0KPHN2ZyB3aWR0aD0iODAwcHgiIGhlaWdodD0iODAwcHgiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCjxwYXRoIGQ9Ik0zLjE3MDA0IDcuNDM5OTRMMTIgMTIuNTQ5OUwyMC43NyA3LjQ2OTkxIiBzdHJva2U9IiMyOTJEMzIiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4NCjxwYXRoIGQ9Ik0xMiAyMS42MDk5VjEyLjUzOTkiIHN0cm9rZT0iIzI5MkQzMiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPg0KPHBhdGggZD0iTTIxLjYxIDEyLjgzVjkuMTdDMjEuNjEgNy43OSAyMC42MiA2LjExMDAyIDE5LjQxIDUuNDQwMDJMMTQuMDcgMi40OEMxMi45MyAxLjg0IDExLjA3IDEuODQgOS45Mjk5OSAyLjQ4TDQuNTkgNS40NDAwMkMzLjM4IDYuMTEwMDIgMi4zOTAwMSA3Ljc5IDIuMzkwMDEgOS4xN1YxNC44M0MyLjM5MDAxIDE2LjIxIDMuMzggMTcuODkgNC41OSAxOC41Nkw5LjkyOTk5IDIxLjUyQzEwLjUgMjEuODQgMTEuMjUgMjIgMTIgMjJDMTIuNzUgMjIgMTMuNSAyMS44NCAxNC4wNyAyMS41MiIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8cGF0aCBkPSJNMTkuMiAyMS40QzIwLjk2NzMgMjEuNCAyMi40IDE5Ljk2NzMgMjIuNCAxOC4yQzIyLjQgMTYuNDMyNyAyMC45NjczIDE1IDE5LjIgMTVDMTcuNDMyNyAxNSAxNiAxNi40MzI3IDE2IDE4LjJDMTYgMTkuOTY3MyAxNy40MzI3IDIxLjQgMTkuMiAyMS40WiIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8cGF0aCBkPSJNMjMgMjJMMjIgMjEiIHN0cm9rZT0iIzI5MkQzMiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPg0KPC9zdmc+",
      "gpt-openapi" to "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48IS0tIFVwbG9hZGVkIHRvOiBTVkcgUmVwbywgd3d3LnN2Z3JlcG8uY29tLCBHZW5lcmF0b3I6IFNWRyBSZXBvIE1peGVyIFRvb2xzIC0tPg0KPHN2ZyB3aWR0aD0iODAwcHgiIGhlaWdodD0iODAwcHgiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCjxwYXRoIGQ9Ik0xMiAyMkMxNy41MjI4IDIyIDIyIDE3LjUyMjggMjIgMTJDMjIgNi40NzcxNSAxNy41MjI4IDIgMTIgMkM2LjQ3NzE1IDIgMiA2LjQ3NzE1IDIgMTJDMiAxNy41MjI4IDYuNDc3MTUgMjIgMTIgMjJaIiBzdHJva2U9IiMyOTJEMzIiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4NCjxwYXRoIGQ9Ik03Ljk5OTk4IDNIOC45OTk5OEM3LjA0OTk4IDguODQgNy4wNDk5OCAxNS4xNiA4Ljk5OTk4IDIxSDcuOTk5OTgiIHN0cm9rZT0iIzI5MkQzMiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPg0KPHBhdGggZD0iTTE1IDNDMTYuOTUgOC44NCAxNi45NSAxNS4xNiAxNSAyMSIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8cGF0aCBkPSJNMyAxNlYxNUM4Ljg0IDE2Ljk1IDE1LjE2IDE2Ljk1IDIxIDE1VjE2IiBzdHJva2U9IiMyOTJEMzIiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4NCjxwYXRoIGQ9Ik0zIDkuMDAwMUM4Ljg0IDcuMDUwMSAxNS4xNiA3LjA1MDEgMjEgOS4wMDAxIiBzdHJva2U9IiMyOTJEMzIiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4NCjwvc3ZnPg==",
      "gpt-retrieval" to "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48IS0tIFVwbG9hZGVkIHRvOiBTVkcgUmVwbywgd3d3LnN2Z3JlcG8uY29tLCBHZW5lcmF0b3I6IFNWRyBSZXBvIE1peGVyIFRvb2xzIC0tPg0KPHN2ZyB3aWR0aD0iODAwcHgiIGhlaWdodD0iODAwcHgiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCjxwYXRoIGQ9Ik0xNyAxOC40MzAxSDEzTDguNTQ5OTkgMjEuMzlDNy44ODk5OSAyMS44MyA3IDIxLjM2MDEgNyAyMC41NjAxVjE4LjQzMDFDNCAxOC40MzAxIDIgMTYuNDMwMSAyIDEzLjQzMDFWNy40Mjk5OUMyIDQuNDI5OTkgNCAyLjQyOTk5IDcgMi40Mjk5OUgxN0MyMCAyLjQyOTk5IDIyIDQuNDI5OTkgMjIgNy40Mjk5OVYxMy40MzAxQzIyIDE2LjQzMDEgMjAgMTguNDMwMSAxNyAxOC40MzAxWiIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4NCjxwYXRoIGQ9Ik0xMi4wMDAxIDExLjM2VjExLjE1QzEyLjAwMDEgMTAuNDcgMTIuNDIwMSAxMC4xMSAxMi44NDAxIDkuODIwMDFDMTMuMjUwMSA5LjU0MDAxIDEzLjY2IDkuMTgwMDIgMTMuNjYgOC41MjAwMkMxMy42NiA3LjYwMDAyIDEyLjkyMDEgNi44NTk5OSAxMi4wMDAxIDYuODU5OTlDMTEuMDgwMSA2Ljg1OTk5IDEwLjM0MDEgNy42MDAwMiAxMC4zNDAxIDguNTIwMDIiIHN0cm9rZT0iIzI5MkQzMiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPg0KPHBhdGggZD0iTTExLjk5NTUgMTMuNzVIMTIuMDA0NSIgc3Ryb2tlPSIjMjkyRDMyIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8L3N2Zz4="
    )
  }

  fun createProcess(
    elementDefinitions: List<Element>,
    flowDefinitions: List<Flow>,
  ): String? {
    // Create adjacency list for depth-first creation of process
    for (flowDefinition in flowDefinitions) {
      val from = flowDefinition.from
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
        val toNodeName = outgoingFlowDefinition.to
        val fromNode = nodeBuilders[fromNodeName]!!
        val condition = outgoingFlowDefinition.condition

        if (!condition.isNullOrEmpty()) {
          fromNode.condition(condition.toFeelExpression())
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

    val modelInstance = processBuilder.done()

    val client = ZeebeClient.newClientBuilder().usePlaintext().build()

    val res = client.newDeployResourceCommand()
      .addProcessModel(modelInstance, UUID.randomUUID().toString() + ".bpmn")
      .send().join()

    return res.processes.first().bpmnProcessId
  }

  private fun createNode(elementDefinitions: List<Element>, toNodeName: String, nodeName: String) {
    val toNodeDefinition = elementDefinitions.findByName(toNodeName)
      ?: throw IllegalStateException("Flow target $toNodeName not found.")

    val type = toNodeDefinition.type
    val name = toNodeDefinition.name
    var builder = nodeBuilders[nodeName]!!

    builder = when (type) {
      "user_task" -> builder
        .userTask(toNodeDefinition.name)
        .zeebeUserTaskForm(
          FormGenerator.generate(toNodeDefinition.instruction ?: "", toNodeDefinition.input_variables)
        )
      "end" -> builder.endEvent(name)
      "gateway" -> builder.exclusiveGateway(name)
      else -> createServiceTask(builder, toNodeDefinition)
    }
    nodeBuilders[name] = builder
  }

  private fun createStartEvent(elementDefinitions: List<Element>, processBuilder: ProcessBuilder) =
    elementDefinitions.findStartEvent()
      ?.let { startDefinition ->
        val name = startDefinition.name
        val startEventBuilder = processBuilder.startEvent(name)
        nodeBuilders[name] = startEventBuilder
        name
      } ?: throw IllegalArgumentException("No start event found")

  private fun createServiceTask(builder: AbstractFlowNodeBuilder<*, *>, elementDefinition: Element): ServiceTaskBuilder {
    val activityDefinition = activityDefinitions[elementDefinition.type]
      ?: throw IllegalStateException("No activity definition for element type ${elementDefinition.type}.")

    val serviceTaskBuilder = builder
      .serviceTask(elementDefinition.name)
      .zeebeJobType(activityDefinition.task)

    // is connector?
    if (activityDefinition.task in templates.keys) {
      addDefaultInputs(serviceTaskBuilder, elementDefinition)
      addInputsFromAttributes(serviceTaskBuilder, activityDefinition.attributes)
      addConnectorTemplate(serviceTaskBuilder, elementDefinition)
    }
    return serviceTaskBuilder
  }

  private fun addInputsFromAttributes(serviceTaskBuilder: ServiceTaskBuilder, attributes: Map<String, String>) {
    attributes.entries.forEach {
      serviceTaskBuilder.zeebeInput(it.value, it.key)
    }
  }

  private fun addDefaultInputs(serviceTaskBuilder: ServiceTaskBuilder, elementDefinition: Element) {
    val inputVarMap = elementDefinition.input_variables.associateBy({it}) { it }
    serviceTaskBuilder
      .zeebeInput("secrets.OPENAI_API_KEY", "apiKey")
      .zeebeInput("GPT_4", "model")
      .zeebeInput("=" + objectMapper.writeValueAsString(inputVarMap).replace("\"", ""), "inputJson")
      .zeebeInput(elementDefinition.instruction, "query")

    if (elementDefinition.output_variable != null && elementDefinition.output_schema != null) {
      serviceTaskBuilder.zeebeTaskHeader("resultExpression", "={" + elementDefinition.output_variable + ": result}")
      serviceTaskBuilder.zeebeInput("=" + objectMapper.writeValueAsString(elementDefinition.output_schema), "outputSchema")
    }
  }

  private fun addDatabaseConnectorAttributes(serviceTaskBuilder: ServiceTaskBuilder, elementDefinition: Element, activity: ActivityDefinition) {
    serviceTaskBuilder
      .zeebeInput(activity.attributes["databaseUrl"], "databaseUrl")
      .zeebeInput("NULL", "missingDataBehavior")
  }

  private fun registerNamespaces(processBuilder: ProcessBuilder) {
    val root = processBuilder.element.modelInstance.document.rootElement
    root.registerNamespace("zeebe", ZEEBE_SCHEMA)
    root.registerNamespace("modeler", MODELER_SCHEMA)
  }

  private fun addConnectorTemplate(builder: AbstractFlowNodeBuilder<*, *>, elementDefinition: Element) {
    val dom = builder.element.domElement
    dom.setAttribute(ZEEBE_SCHEMA, "modelerTemplate", templates[activityDefinitions[elementDefinition.type]!!.task!!]!!)
    dom.setAttribute(ZEEBE_SCHEMA, "modelerTemplateVersion", "1")
    dom.setAttribute(ZEEBE_SCHEMA, "modelerTemplateIcon", icons[activityDefinitions[elementDefinition.type]!!.task!!]!!)
  }

  private fun String.toFeelExpression(): String {
    val feel = if (startsWith("!")) {
      this.drop(1) + " = false"
    } else this
    return "=$feel"
  }

  ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  private fun writeModelToFile(modelInstance: BpmnModelInstance?, filePath: String) {
    try {
      val file = File(filePath)
      Bpmn.writeModelToFile(file, modelInstance)
    } catch (e: Exception) {
      throw RuntimeException("Failed to write BPMN model to file: $filePath", e)
    }
  }
}

