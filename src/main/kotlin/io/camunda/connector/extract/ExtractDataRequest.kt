package io.camunda.connector.extract

import io.camunda.connector.api.annotation.Secret

data class ExtractDataRequest(
    var context: String? = null,
    var description: String? = null,

    @Secret var apiKey: String? = null
)
