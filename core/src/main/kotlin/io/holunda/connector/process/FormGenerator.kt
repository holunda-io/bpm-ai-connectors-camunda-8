package io.holunda.connector.process

import java.util.*

object FormGenerator {

  fun generate(task: String, variables: List<String>): String {

    fun getField(name: String) = """
      {
          "text": "=\"$name: \" + string($name)",
          "type": "text",
          "id": "${UUID.randomUUID()}"
      }
    """.trimIndent()

    return """
    {
      "components": [
        {
          "text": "$task",
          "type": "text",
          "id": "Field_1iuiyym"
        },
        ${variables.joinToString(",") { getField(it) }},
        {
          "label": "Result",
          "type": "textarea",
          "id": "Field_02um984",
          "key": "answer"
        },
        {
          "action": "submit",
          "label": "Submit",
          "type": "button",
          "id": "Field_0mk7v9s",
          "key": "field_1g36id3",
          "conditional": {
            "hide": "=answer = \"\""
          }
        }
      ],
      "type": "default",
      "id": "Form_1rw7thd",
      "executionPlatform": "Camunda Cloud",
      "executionPlatformVersion": "8.1.0",
      "exporter": {
        "name": "Camunda Modeler",
        "version": "5.9.0"
      },
      "schemaVersion": 7
    }
  """.trimIndent()
  }

}
