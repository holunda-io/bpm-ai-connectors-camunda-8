package io.camunda.connector.common.openai

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import com.aallam.openai.api.http.*
import com.aallam.openai.api.model.*
import com.aallam.openai.client.*
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds

@OptIn(BetaOpenAI::class)
class OpenAIClient(@Value("\${openai.apikey}") apiKey: String) {

    private val openAI = OpenAI(OpenAIConfig(
        token = apiKey,
        timeout = Timeout(socket = 60.seconds)
    ))

    fun getModels() = runBlocking { openAI.models() }

    fun chatCompletion(
        promptMessages: List<ChatMessage>,
        chatHistory: List<ChatMessage> = emptyList(),
        modelId: ModelId? = null
    ): List<ChatMessage> = runBlocking {
        val messages = chatHistory + promptMessages

        val chatCompletionRequest = ChatCompletionRequest(
            model = modelId ?: ModelId(DEFAULT_MODEL_ID),
            messages = messages
        )

        openAI.chatCompletion(chatCompletionRequest)
            .first()
            ?.let { completionMessage -> messages + completionMessage }
            ?: throw OpenAIException("No result message")
    }

    companion object {
        const val DEFAULT_MODEL_ID = "gpt-3.5-turbo"
    }
}

@OptIn(BetaOpenAI::class)
fun List<ChatMessage>.latest() = this.last().content

@OptIn(BetaOpenAI::class)
fun ChatCompletion.first() = this.choices.first().message

class OpenAIException(message: String) : RuntimeException(message)