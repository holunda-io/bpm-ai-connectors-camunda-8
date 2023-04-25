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
        val c = openAIClient.chatCompletion(buildFixingPrompt(), history)
        return outputParser.parse(c.completionContent())
    }

    private fun buildFixingPrompt() = listOf(
        ChatMessage(
            ChatRole.User,
            FIXING_PROMPT
        )
    )

    companion object {
        private val FIXING_PROMPT = """
            There was an error parsing your response. 
            Make sure you provide a valid JSON with the "result" and "reasoning" fields populated as specified above.
            
            Try again:
        """.trimIndent()
    }
}