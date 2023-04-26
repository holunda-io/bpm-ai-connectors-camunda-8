package io.holunda.connector.common.openai

import com.aallam.openai.api.model.*

enum class Model(val modelId: ModelId) {
    GPT_3(ModelId("gpt-3.5-turbo")),
    GPT_4(ModelId("gpt-4")),
    CUSTOM(ModelId("custom"))
}