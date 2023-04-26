package io.holunda.connector.extract

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import io.holunda.connector.common.prompt.*

@OptIn(BetaOpenAI::class)
class ExtractPrompt(
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
            USER_PROMPT.format(inputJson)
        ),
    )

    companion object {
        private val SYSTEM_PROMPT = """
            You are an extremely clever data extraction AI. You love to extract data and information from an input text and output correct results. 
            
            You will receive a JSON with input values to extract information from.
            If the input JSON does not contain some of the required information, set the corresponding value in the result to null.
            
            %s
        """.trimIndent()

        private val USER_PROMPT = """            
            INPUT:
            ```
            %s
            ```
            
            EXTRACTED INFORMATION:
        """.trimIndent()
    }
}