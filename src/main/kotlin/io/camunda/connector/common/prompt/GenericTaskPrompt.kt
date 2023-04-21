package io.camunda.connector.common.prompt

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import com.google.gson.*
import com.google.gson.reflect.*

@OptIn(BetaOpenAI::class)
class GenericTaskPrompt(
    private val taskDescription: String,
    private val inputVariables: Map<String, Any?>,
    private val formatInstructions: String
) : Prompt {

    override fun buildPrompt() = listOf(
        ChatMessage(
            ChatRole.System,
            SYSTEM_PROMPT.format(formatInstructions)
        ),
        ChatMessage(
            ChatRole.User,
            USER_PROMPT.format(taskDescription, gson.toJson(inputVariables))
        ),
    )

    private val gson = Gson()

    companion object {
        private val SYSTEM_PROMPT = """
            You are an extremely clever business AI that loves to make smart decisions and give correct results. 

            Your job is to help users execute their business processes in a smart and efficient way.
            
            You will receive a task description and a JSON with input values for the task.
            
            %s
        """.trimIndent()

        private val USER_PROMPT = """
            TASK DESCRIPTION:
            ```
            %s
            ```
            
            INPUT:
            ```
            %s
            ```
        """.trimIndent()
    }
}