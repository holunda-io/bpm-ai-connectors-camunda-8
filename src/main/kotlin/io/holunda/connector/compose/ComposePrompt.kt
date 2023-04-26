package io.holunda.connector.compose

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import io.holunda.connector.common.prompt.*

@OptIn(BetaOpenAI::class)
class ComposePrompt(
    private val description: String,
    private val style: String,
    private val tone: String,
    private val language: String,
    private val sender: String,
    private val inputJson: String,
) : Prompt {

    override fun buildPrompt() = listOf(
        ChatMessage(
            ChatRole.System,
            SYSTEM_PROMPT
        ),
        ChatMessage(
            ChatRole.User,
            USER_PROMPT.format(inputJson, description, style, tone, language, sender)
        ),
    )

    companion object {
        private val SYSTEM_PROMPT = """
            You are a creative writing AI that loves to compose %s texts for emails or letters that have a %s tone.
            You are an expert for writing in %s.

            Your job is to compose a text based on instructions, input data and desired text properties.
            Add a salutation and complimentary close that fits the desired style and tone.
            Only use information from the given instructions, properties and input data, do not make something up.
            Only output the result text and nothing else.
        """.trimIndent()

        private val USER_PROMPT = """           
            INPUT DATA:
            ```
            %s
            ```
            
            INSTRUCTIONS:
            ```
            %s
            ```
            
            TEXT PROPERTIES:
            - style: %s
            - tone: %s
            - language: %s
            - sender: %s
            
            RESULT TEXT:
        """.trimIndent()
    }
}