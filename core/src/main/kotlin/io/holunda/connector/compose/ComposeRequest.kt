package io.holunda.connector.compose

import com.fasterxml.jackson.databind.*
import io.holunda.connector.common.*

data class ComposeRequest(
    val inputJson: JsonNode,
    var description: String,
    val properties: TextProperties,
    val sender: String?,
    val template: String?,
    val alignment: AlignmentPrinciple,
    val model: Model
)

data class TextProperties(
    val style: String,
    val type: String,
    val tone: String,
    val length: String,
    val language: String,
    val temperature: Double = 0.0,
)

data class AlignmentPrinciple(
    val constitutionalPrinciple: String?,
    val customPrinciple: String?
)
