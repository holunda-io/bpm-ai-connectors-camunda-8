package io.holunda.connector.common.openai

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import com.aallam.openai.api.http.*
import com.aallam.openai.api.model.*
import com.aallam.openai.client.*
import io.ktor.client.*
import io.ktor.client.request.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds

@OptIn(BetaOpenAI::class)
class OpenAIClient(apiKey: String) {

    private val openAI = OpenAI(OpenAIConfig(
        token = apiKey,
        timeout = Timeout(socket = (60 * 5).seconds)
    ))

    fun getModels() = runBlocking { openAI.models() }

    fun chatCompletion(
        promptMessages: List<ChatMessage>,
        chatHistory: List<ChatMessage> = emptyList(),
        model: Model = defaultModel
    ): List<ChatMessage> = runBlocking {
        val messages = chatHistory + promptMessages

        val chatCompletionRequest = ChatCompletionRequest(
          model = model.modelId,
          messages = messages,
          temperature = 0.0
        )

        if (model == Model.CUSTOM) throw NotImplementedError("Custom models are not yet supported")

        openAI.chatCompletion(chatCompletionRequest)
            .first()
            ?.let { completionMessage -> messages + completionMessage }
            ?: throw OpenAIException("No result message")
    }

    companion object {
        val defaultModel = Model.GPT_3
    }
}

@OptIn(BetaOpenAI::class)
fun List<ChatMessage>.completionContent() = this.last().content

@OptIn(BetaOpenAI::class)
fun ChatCompletion.first() = this.choices.first().message

class OpenAIException(message: String) : RuntimeException(message)
