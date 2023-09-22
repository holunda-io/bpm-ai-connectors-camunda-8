package io.holunda.connector.extract

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.mockk.*
import org.junit.jupiter.api.*

class ExtractFunctionTest : AbstractFunctionTest<ExtractFunction>() {

    override val function = ExtractFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<ExtractRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        every { mockRequest.extractionJson } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, ExtractRequest::class.java)

        verify { ExtractTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(ExtractResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as ExtractResult).result)
    }
}
