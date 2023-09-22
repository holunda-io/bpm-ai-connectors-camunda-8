package io.holunda.connector.openapi

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.holunda.connector.database.*
import io.holunda.connector.openapi.*
import io.mockk.*
import org.junit.jupiter.api.*

class OpenApiAgentFunctionTest : AbstractFunctionTest<OpenApiAgentFunction>() {

    override val function = OpenApiAgentFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<OpenApiAgentRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        every { mockRequest.outputSchema } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, OpenApiAgentRequest::class.java)

        verify { OpenApiAgentTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(OpenApiAgentResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as OpenApiAgentResult).result)
    }
}
