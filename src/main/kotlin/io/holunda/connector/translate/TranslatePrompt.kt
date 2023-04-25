package io.holunda.connector.translate

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import com.google.gson.*
import com.google.gson.reflect.*
import io.holunda.connector.common.prompt.*

@OptIn(BetaOpenAI::class)
class TranslatePrompt(
    private val inputJson: String,
    private val language: String,
    private val formatInstructions: String
) : Prompt {

    override fun buildPrompt() = listOf(
        ChatMessage(
            ChatRole.System,
            SYSTEM_PROMPT.format(language, language, formatInstructions)
        ),
        ChatMessage(
            ChatRole.User,
            USER_PROMPT.format(inputJson, language.uppercase())
        ),
    )

    companion object {
        private val SYSTEM_PROMPT = """
            You are an extremely clever translation AI that loves to correctly translate texts from any language into %s. 

            Your job is to translate the values of a given input JSON into %s.
            You will only translate the values and leave the field names untouched.
           
            %s
        """.trimIndent()

        private val USER_PROMPT = """          
            INPUT:
            ```
            %s
            ```
            
            TRANSLATED INTO %s:
        """.trimIndent()
    }
}