package io.camunda.connector.common.prompt

interface OutputParser<R> {

    fun getFormatInstructions(): String

    fun parse(completion: String): R

}