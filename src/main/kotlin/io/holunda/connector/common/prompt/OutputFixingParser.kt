package io.holunda.connector.common.prompt

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import io.holunda.connector.common.openai.*

@OptIn(BetaOpenAI::class)
class OutputFixingParser<R>(
    private val prompt: Prompt,
    private val outputParser: OutputParser<R>,
    private val openAIClient: OpenAIClient
) : OutputParser<R> {

    override fun getFormatInstructions() = outputParser.getFormatInstructions()

    override fun parse(completion: String): R {
        return try {
            outputParser.parse(completion)
        } catch (e: Exception) {
            return tryToFixOutput(completion)
        }
    }

    private fun tryToFixOutput(completion: String): R {
        val history = prompt.buildPrompt() + ChatMessage(ChatRole.Assistant, completion)
        val completedHistory = openAIClient.chatCompletion(buildFixingPrompt(), history)
        return outputParser.parse(completedHistory.completionContent())
    }

    private fun buildFixingPrompt() = listOf(
        ChatMessage(
            ChatRole.User,
            FIXING_PROMPT.format(getFormatInstructions())
        )
    )

    companion object {
        private val FIXING_PROMPT = """
            There was an error parsing your response. 
           
            %s
            
            Try again:
        """.trimIndent()
    }
}