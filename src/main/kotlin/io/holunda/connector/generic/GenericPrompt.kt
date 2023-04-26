package io.holunda.connector.generic

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import io.holunda.connector.common.prompt.*

@OptIn(BetaOpenAI::class)
class GenericPrompt(
    private val taskDescription: String,
    private val inputJson: String,
    private val formatInstructions: String
) : Prompt {

    override fun buildPrompt() = listOf(
        ChatMessage(
            ChatRole.System,
            SYSTEM_PROMPT.format(formatInstructions)
        ),
        ChatMessage(
            ChatRole.User,
            USER_PROMPT.format(taskDescription, inputJson)
        ),
    )

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