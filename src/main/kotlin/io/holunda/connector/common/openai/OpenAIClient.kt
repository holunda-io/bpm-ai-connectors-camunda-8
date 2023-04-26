package io.holunda.connector.common.openai

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import com.aallam.openai.api.http.*
import com.aallam.openai.api.model.*
import com.aallam.openai.client.*
import io.holunda.connector.common.openai.Model.*
import io.ktor.client.*
import io.ktor.client.request.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds

@OptIn(BetaOpenAI::class)
class OpenAIClient(val apiKey: String) {

    fun chatCompletion(
        promptMessages: List<ChatMessage>,
        chatHistory: List<ChatMessage> = emptyList(),
        model: Model = defaultModel,
        host: OpenAIHost = OpenAIHost.OpenAI
    ): List<ChatMessage> = runBlocking {
        val messages = chatHistory + promptMessages

        val chatCompletionRequest = ChatCompletionRequest(
            model = model.modelId,
            messages = messages
        )

        val client = OpenAI(OpenAIConfig(
            token = apiKey,
            timeout = timeout,
            host = host
        ))

        client.chatCompletion(chatCompletionRequest)
            .first()
            ?.let { completionMessage -> messages + completionMessage }
            ?: throw OpenAIException("No result message")
    }

    companion object {
        val defaultModel = GPT_3
        val timeout = Timeout(socket = (60 * 5).seconds)
    }
}

@OptIn(BetaOpenAI::class)
fun List<ChatMessage>.completionContent() = this.last().content

@OptIn(BetaOpenAI::class)
fun ChatCompletion.first() = this.choices.first().message

class OpenAIException(message: String) : RuntimeException(message)