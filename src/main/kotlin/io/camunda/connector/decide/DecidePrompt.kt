package io.camunda.connector.decide

import com.aallam.openai.api.*
import com.aallam.openai.api.chat.*
import com.google.gson.*
import com.google.gson.reflect.*
import io.camunda.connector.common.prompt.*

@OptIn(BetaOpenAI::class)
class DecidePrompt(
    private val inputJson: String,
    private val instructions: String,
    private val outputType: String,
    private val possibleValues: String?,
    private val formatInstructions: String
) : Prompt {

    override fun buildPrompt() = listOf(
        ChatMessage(
            ChatRole.System,
            SYSTEM_PROMPT.format(formatInstructions)
        ),
        ChatMessage(
            ChatRole.User,
            USER_PROMPT.format(
                instructions,
                outputType,
                possibleValues?.let { "\nPOSSIBLE VALUES:\n$it\n\n Your decision can only be one of these possible values or null." } ?: "",
                inputJson,
                possibleValues
            )
        ),
    )

    companion object {
        private val SYSTEM_PROMPT = """
            You are an extremely clever business AI that loves to make smart decisions and give correct results. 

            Your job is to help users execute their business processes in a smart and efficient way by making smart decisions. 
            
            You will receive a decision task description and a JSON with input values to base your decision on.
            Make a decision based on the decision task description and input data.
            If the input JSON does not contain sufficient information, your decision will be null.
            
            %s
        """.trimIndent()

        private val USER_PROMPT = """   
            DECISION TASK DESCRIPTION:
            ```
            %s
            ```    
                 
            DECISION OUTPUT TYPE:
            %s
            %s
                    
            INPUT:
            ```
            %s
            ```
            
            DECISION:
        """.trimIndent()
    }
}