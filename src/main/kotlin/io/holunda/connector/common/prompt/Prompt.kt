package io.holunda.connector.common.prompt

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*

@OptIn(BetaOpenAI::class)
interface Prompt {

    fun buildPrompt(): List<ChatMessage>

}